"""Searcher Agent for web crawling and information collection."""

import time
import json
import re
import requests
from datetime import datetime, timedelta, timezone
from urllib.parse import urljoin

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from webdriver_manager.chrome import ChromeDriverManager
from selenium.common.exceptions import StaleElementReferenceException, NoSuchElementException, TimeoutException
from selenium.webdriver.support.ui import WebDriverWait, Select
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.action_chains import ActionChains

from bs4 import BeautifulSoup

from .base_agent import BaseAgent
from ..state import WorkflowState

from .base_agent import BaseAgent
from ..state import WorkflowState

class WebSearcher:
    def __init__(self, perplexity_api_key: str = None):
        self.driver = None
        self.perplexity_api_key = perplexity_api_key or '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'
        self.setup_driver()
    
    def setup_driver(self):
        """WebDriver 설정"""
        print("WebDriver 설정을 시작합니다...")
        chrome_options = Options()
        # chrome_options.add_argument("--headless")
        chrome_options.add_argument("--start-maximized")
        chrome_options.add_argument("user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36")
        chrome_options.add_argument("--disable-blink-features=AutomationControlled")
        chrome_options.add_experimental_option("excludeSwitches", ["enable-automation"])
        chrome_options.add_experimental_option('useAutomationExtension', False)
        
        service = Service(ChromeDriverManager().install())
        self.driver = webdriver.Chrome(service=service, options=chrome_options)
        print("WebDriver 설정이 완료되었습니다.")
    
    def close_driver(self):
        """WebDriver 종료"""
        if self.driver:
            self.driver.quit()
            print("WebDriver를 종료합니다.")
    
    def crawl_pytorch_kr(self):
        """파이토치 한국 사용자 모임 크롤링"""
        print("\n=== 파이토치 한국 사용자 모임 크롤링 시작 ===")
        
        URL = "https://discuss.pytorch.kr/c/news"
        self.driver.get(URL)
        print(f"'{URL}' 페이지로 이동합니다.")
        time.sleep(3)

        one_week_ago = datetime.now() - timedelta(days=7)
        post_info = {}

        print("\n최신 게시글 수집을 시작합니다 (스크롤 다운)...")
        while True:
            topic_list_items = self.driver.find_elements(By.CSS_SELECTOR, "tbody.topic-list-body tr.topic-list-item")
            
            if not topic_list_items:
                print("게시글을 찾을 수 없습니다.")
                break

            last_post_date = None
            
            for item in topic_list_items:
                try:
                    date_span = item.find_element(By.CSS_SELECTOR, "span.relative-date")
                    post_timestamp_ms = int(date_span.get_attribute("data-time"))
                    post_date = datetime.fromtimestamp(post_timestamp_ms / 1000)
                    
                    last_post_date = post_date
                    
                    if post_date >= one_week_ago:
                        link_element = item.find_element(By.CSS_SELECTOR, "a.title")
                        link = link_element.get_attribute("href")
                        if link not in post_info:
                            post_info[link] = post_date
                    
                except (StaleElementReferenceException, NoSuchElementException):
                    continue

            print(f"현재까지 수집된 링크 수: {len(post_info)}")

            if last_post_date and last_post_date < one_week_ago:
                print("일주일 이전 게시글에 도달하여 스크롤을 중단합니다.")
                break
                
            self.driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
            time.sleep(2)

        crawled_data = []
        print(f"\n총 {len(post_info)}개의 최신 뉴스에 대한 크롤링을 시작합니다.")

        for link, post_date in post_info.items():
            try:
                self.driver.get(link)
                time.sleep(2)

                title_element = self.driver.find_element(By.CSS_SELECTOR, "a.fancy-title")
                title = title_element.text

                post_content_element = self.driver.find_element(By.CSS_SELECTOR, "article#post_1 div.cooked")
                content_text = post_content_element.text
                
                formatted_date = post_date.strftime("%Y-%m-%d")
                
                crawled_data.append({
                    "title": title,
                    "url": link,
                    "content": content_text,
                    "date": formatted_date,
                    "source": "파이토치 한국 사용자 모임",
                    "category": "기술"
                })
                
                print(f"✅ 제목: {title}")
                print(f"   날짜: {formatted_date}")
                print(f"   URL: {link}\n")
                
            except Exception as e:
                print(f"❌ URL {link} 크롤링 중 오류 발생: {e}")

        print(f"파이토치 한국 사용자 모임 크롤링 완료! 총 {len(crawled_data)}개의 데이터를 수집했습니다.")
        return crawled_data

    def crawl_techcrunch(self):
        """TechCrunch 크롤링"""
        print("\n=== TechCrunch 크롤링 시작 ===")
        
        URL = "https://techcrunch.com/category/artificial-intelligence/"
        self.driver.get(URL)
        time.sleep(3) 

        one_week_ago = datetime.now(timezone.utc) - timedelta(days=7)
        article_data = {} 
        processed_articles_on_page = set()

        while True:
            articles = self.driver.find_elements(By.CSS_SELECTOR, "li.wp-block-post")
            
            stop_crawling = False
            
            for article in articles:
                try:
                    link_element = article.find_element(By.CSS_SELECTOR, "h3 a")
                    link = link_element.get_attribute("href")
                    
                    if link in processed_articles_on_page:
                        continue
                    
                    processed_articles_on_page.add(link)

                    date_element = article.find_element(By.CSS_SELECTOR, "time")
                    date_str_iso = date_element.get_attribute("datetime")
                    article_date = datetime.fromisoformat(date_str_iso)
                    
                    if article_date < one_week_ago:
                        print("일주일 이전 기사에 도달하여 수집을 중단합니다.")
                        stop_crawling = True
                        break
                    
                    formatted_date = article_date.strftime('%Y-%m-%d')
                    article_data[link] = formatted_date
                    
                except (StaleElementReferenceException, NoSuchElementException):
                    continue
            
            print(f"현재까지 수집된 링크 수: {len(article_data)}")
            
            if stop_crawling:
                break

            try:
                next_button = self.driver.find_element(By.CSS_SELECTOR, "a.wp-block-query-pagination-next")
                print("다음 페이지로 이동합니다...")
                self.driver.execute_script("arguments[0].click();", next_button)
                processed_articles_on_page.clear()
                time.sleep(3)
            except NoSuchElementException:
                print("'Next' 버튼을 찾을 수 없어 크롤링을 종료합니다.")
                break

        crawled_data = []
        print(f"\n총 {len(article_data)}개의 최신 기사에 대한 크롤링을 시작합니다.")

        for link, date_str in article_data.items():
            try:
                self.driver.get(link)
                time.sleep(2)

                title = self.driver.find_element(By.CSS_SELECTOR, "h1.wp-block-post-title").text
                content = self.driver.find_element(By.CSS_SELECTOR, "div.entry-content").text
                
                crawled_data.append({
                    "title": title,
                    "url": link,
                    "content": content,
                    "date": date_str,
                    "source": "TechCrunch",
                    "category": "산업"
                })
                
                print(f"✅ 제목: {title}")
                print(f"   날짜: {date_str}")
                print(f"   (URL: {link})\n")
                
            except Exception as e:
                print(f"❌ URL {link} 크롤링 중 오류 발생: {e}")

        print(f"TechCrunch 크롤링 완료! 총 {len(crawled_data)}개의 기사를 수집했습니다.")
        return crawled_data

    def crawl_huggingface(self):
        """HuggingFace Trending Papers 크롤링"""
        print("\n=== HuggingFace Trending Papers 크롤링 시작 ===")
        
        START_URL = "https://huggingface.co/papers/trending"
        self.driver.get(START_URL)

        try:
            WebDriverWait(self.driver, 15).until(EC.presence_of_element_located((By.TAG_NAME, "article")))
            print("페이지 및 논문 목록 로드 완료.")
        except TimeoutException:
            print("오류: 페이지를 로드하지 못했습니다.")
            return []

        one_week_ago = datetime.now() - timedelta(days=7)
        paper_data = {}
        last_processed_count = 0

        while True:
            papers = self.driver.find_elements(By.TAG_NAME, "article")
            
            if len(papers) == last_processed_count:
                print("새로운 논문이 더 이상 로드되지 않아 스크롤을 중단합니다.")
                break

            stop_crawling = False
            for paper in papers[last_processed_count:]:
                try:
                    all_spans = paper.find_elements(By.TAG_NAME, "span")
                    paper_date_found = False
                    for span in all_spans:
                        try:
                            date_text = span.text.replace("Published on ", "").strip()
                            paper_date = datetime.strptime(date_text, "%b %d, %Y")
                            paper_date_found = True
                            break 
                        except ValueError:
                            continue
                    
                    if paper_date_found:
                        if paper_date < one_week_ago:
                            stop_crawling = True
                            break
                        
                        link_element = paper.find_element(By.CSS_SELECTOR, "h3 a")
                        full_link = link_element.get_attribute("href")
                        paper_data[full_link] = paper_date.strftime('%Y-%m-%d')

                except Exception:
                    continue
            
            print(f"현재까지 수집된 논문 수: {len(paper_data)}")
            
            if stop_crawling:
                print("일주일 이전 논문에 도달하여 수집을 중단합니다.")
                break
            
            last_processed_count = len(papers)
            self.driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
            time.sleep(3)

        crawled_data = []
        print(f"\n총 {len(paper_data)}개의 논문을 크롤링합니다.")

        for link, date_str in paper_data.items():
            try:
                self.driver.get(link)
                abstract_header = WebDriverWait(self.driver, 10).until(
                    EC.presence_of_element_located((By.XPATH, "//h2[text()='Abstract']"))
                )
                
                title = self.driver.find_element(By.CSS_SELECTOR, "h1").text
                abstract_content = abstract_header.find_element(By.XPATH, "./following-sibling::div").text
                
                crawled_data.append({
                    "title": title, 
                    "url": link, 
                    "content": abstract_content, 
                    "date": date_str,
                    "source": "HuggingFace Trending",
                    "category": "기술"
                })
                print(f"✅ 제목: {title}")
            except Exception as e:
                print(f"❌ URL {link} 크롤링 중 오류 발생: {e}")
                
        print(f"HuggingFace Trending Papers 크롤링 완료! 총 {len(crawled_data)}개의 논문을 수집했습니다.")
        return crawled_data

    def crawl_aitimes(self):
        """AI타임즈 크롤링"""
        print("\n=== AI타임즈 크롤링 시작 ===")
        
        target_url = "https://www.aitimes.com/news/articleList.html?sc_section_code=S1N3&view_type=sm"
        self.driver.get(target_url)

        print("\n'더보기'를 클릭하여 기사를 추가로 로딩합니다...")
        for i in range(5):
            try:
                wait = WebDriverWait(self.driver, 10)
                more_button = wait.until(EC.element_to_be_clickable((By.CSS_SELECTOR, "button.list-btn-more")))
                self.driver.execute_script("arguments[0].click();", more_button)
                print(f"'{i+1}번째 '더보기' 클릭. 2초 대기...")
                time.sleep(2)
            except (NoSuchElementException, TimeoutException):
                print("'더보기' 버튼이 없거나 더 이상 활성화되지 않아 로딩을 중단합니다.")
                break

        base_url = "https://www.aitimes.com"
        soup = BeautifulSoup(self.driver.page_source, 'html.parser')
        article_links = []
        for tag in soup.select("h2.altlist-subject > a"):
            href = tag.get('href')
            if href:
                full_url = urljoin(base_url, href)
                article_links.append(full_url)
        article_links = list(dict.fromkeys(article_links))
        print(f"\n총 {len(article_links)}개의 고유한 기사 링크를 수집했습니다. 상세 페이지 확인을 시작합니다.")

        final_results = []
        for i, url in enumerate(article_links):
            print(f"\n[{i+1}/{len(article_links)}] 기사 확인 중: {url}")
            try:
                self.driver.get(url)
                WebDriverWait(self.driver, 15).until(EC.presence_of_element_located((By.CSS_SELECTOR, "h1.heading")))
                article_soup = BeautifulSoup(self.driver.page_source, 'html.parser')

                date_element = None
                date_type = ""

                date_element = article_soup.select_one("div.info-update-origin")
                date_type = "입력"
                if not date_element:
                    date_element = article_soup.find("li", string=lambda text: text and "입력" in text)
                
                if not date_element:
                    date_element = article_soup.select_one("li.info-update.show")
                    date_type = "업데이트"

                if not date_element:
                    print("-> 입력 및 업데이트 날짜 정보를 모두 찾지 못해 건너뜁니다.")
                    continue

                raw_date_text = date_element.get_text(strip=True)
                date_match = re.search(r'(\d{4}\.\d{2}\.\d{2}\s+\d{2}:\d{2})', raw_date_text)
                if not date_match:
                    print(f"-> '{date_type}' 날짜 형식을 찾지 못해 건너뜁니다: {raw_date_text}")
                    continue
                
                date_str_full = date_match.group(1)
                article_date = datetime.strptime(date_str_full, "%Y.%m.%d %H:%M")
                formatted_date = article_date.strftime('%Y-%m-%d')

                if datetime.now() - article_date <= timedelta(days=7):
                    print(f"-> {date_type} 날짜 확인: {formatted_date} (수집 대상)")
                    title = article_soup.select_one("h1.heading").text.strip()
                    content_container = article_soup.select_one("article#article-view-content-div")
                    if content_container:
                        content = "\n".join([p.get_text(strip=True) for p in content_container.find_all("p")])
                    else:
                        content = "본문 내용을 찾을 수 없습니다."
                    
                    final_results.append({
                        "title": title,
                        "url": url,
                        "content": content,
                        "date": formatted_date,
                        "source": "AI타임즈",
                        "category": "산업"
                    })
                else:
                    print(f"-> {date_type} 날짜 확인: {formatted_date} (7일 경과). 수집을 중단합니다.")
                    break

            except Exception as e:
                print(f"-> 기사 처리 중 오류 발생: {e}")
                continue

        print(f"AI타임즈 크롤링 완료! 총 {len(final_results)}개의 기사를 수집했습니다.")
        return final_results

    def crawl_arxiv(self, keyword="AI"):
        """arXiv 크롤링"""
        print(f"\n=== arXiv 크롤링 시작 (키워드: {keyword}) ===")
        
        search_url = "https://arxiv.org/search/advanced"
        one_week_ago = datetime.now() - timedelta(days=7)
        crawled_data = []

        try:
            print(f"논문 검색을 시작합니다: '{keyword}'...")
            self.driver.get(search_url)

            print("고급 검색 옵션을 설정합니다...")
            cs_radio_button = WebDriverWait(self.driver, 10).until(EC.element_to_be_clickable((By.CSS_SELECTOR, "label[for='classification-computer_science']")))
            cs_radio_button.click()
            print("- 주제: Computer Science 선택됨")

            select_field = Select(self.driver.find_element(By.NAME, "terms-0-field"))
            select_field.select_by_value("abstract")
            print("- 검색 필드: Abstract 선택됨")

            search_box = self.driver.find_element(By.NAME, "terms-0-term")
            actions = ActionChains(self.driver)
            actions.move_to_element(search_box).click().send_keys(keyword).perform()
            print(f"- 키워드 '{keyword}' 입력됨")

            search_button = self.driver.find_element(By.CSS_SELECTOR, "button.button.is-link.is-medium")
            search_button.click()
            print("검색을 실행합니다.")

            while True:
                WebDriverWait(self.driver, 10).until(EC.presence_of_element_located((By.CSS_SELECTOR, "li.arxiv-result")))
                print(f"\n현재 페이지에서 논문 정보를 수집합니다 ({self.driver.current_url})...")
                
                papers = self.driver.find_elements(By.CSS_SELECTOR, "li.arxiv-result")
                stop_crawling = False

                for paper in papers:
                    try:
                        date_p_elements = paper.find_elements(By.CSS_SELECTOR, "p.is-size-7")
                        date_text_full = ""
                        for p_element in date_p_elements:
                            if p_element.text.strip().startswith("Submitted"):
                                date_text_full = p_element.text.split('\n')[0]
                                break
                        
                        if not date_text_full:
                            raise NoSuchElementException("Could not find paragraph containing 'Submitted' date information.")

                        paper_date = self.parse_arxiv_date(date_text_full)
                        
                        if paper_date is None or paper_date < one_week_ago:
                            stop_crawling = True
                            print("일주일 이전 논문에 도달하여 수집을 중단합니다.")
                            break
                        
                        title = paper.find_element(By.CSS_SELECTOR, "p.title.is-5").text
                        url = paper.find_element(By.CSS_SELECTOR, "p.list-title > a").get_attribute("href")
                        
                        try:
                            abstract_element = paper.find_element(By.CSS_SELECTOR, "span.abstract-full")
                            content = self.driver.execute_script("return arguments[0].textContent;", abstract_element)
                            content = content.replace(" Less", "").strip()
                        except NoSuchElementException:
                            content = ""
                        
                        crawled_data.append({
                            "title": title, 
                            "url": url, 
                            "content": content, 
                            "date": paper_date.strftime("%Y-%m-%d"),
                            "source": "arXiv",
                            "category": "기술"
                        })
                        print(f"  - 수집됨: {title}")

                    except NoSuchElementException as e:
                        print(f"  - 경고: 다른 형식의 항목을 건너뜁니다.")
                        continue

                if stop_crawling:
                    break
                
                try:
                    next_button = self.driver.find_element(By.CSS_SELECTOR, "a.pagination-next")
                    next_button.click()
                except NoSuchElementException:
                    print("\n마지막 페이지에 도달했습니다. 크롤링을 종료합니다.")
                    break

        except TimeoutException:
            print("페이지 시간 초과 또는 검색 결과를 찾을 수 없습니다.")
        except Exception as e:
            print(f"크롤링 중 오류가 발생했습니다: {e}")

        print(f"arXiv 크롤링 완료! 총 {len(crawled_data)}개의 논문을 수집했습니다.")
        return crawled_data

    def parse_arxiv_date(self, date_string):
        """arXiv 날짜 문자열을 datetime 객체로 변환"""
        try:
            clean_date_str = date_string.replace('Submitted ', '').split(';')[0].strip()
            return datetime.strptime(clean_date_str, '%d %B, %Y')
        except (ValueError, IndexError):
            return None

    def crawl_aitimes_kr(self):
        """인공지능 신문 크롤링"""
        print("\n=== 인공지능 신문 크롤링 시작 ===")
        
        list_url = "https://www.aitimes.kr/news/articleList.html?sc_section_code=S1N2&view_type=sm"
        
        print(f"기사 목록 페이지로 이동합니다: {list_url}")
        self.driver.get(list_url)
        
        try:
            WebDriverWait(self.driver, 15).until(lambda d: d.find_elements(By.CSS_SELECTOR, "h4.titles a, a.list-title"))
            print("페이지 로딩 완료.")
        except TimeoutException:
            print("페이지 로딩 시간 초과 또는 기사 제목 링크를 찾을 수 없습니다.")
            return []

        article_links_count = len(self.driver.find_elements(By.CSS_SELECTOR, "h4.titles a, a.list-title"))
        print(f"페이지에서 총 {article_links_count}개의 기사 링크를 발견했습니다.")

        final_results = []
        
        for i in range(article_links_count):
            try:
                WebDriverWait(self.driver, 15).until(EC.presence_of_element_located((By.CSS_SELECTOR, "h4.titles a, a.list-title")))
                links = self.driver.find_elements(By.CSS_SELECTOR, "h4.titles a, a.list-title")
                
                link_text = links[i].text
                print(f"\n[{i+1}/{article_links_count}] '{link_text}' 기사를 클릭합니다.")
                links[i].click()

                WebDriverWait(self.driver, 15).until(EC.presence_of_element_located((By.CSS_SELECTOR, "h3.heading")))
                article_soup = BeautifulSoup(self.driver.page_source, 'html.parser')
                
                date_info_element = article_soup.select_one("ul.infomation li:nth-child(2)")
                if not date_info_element:
                    print("상세 페이지에서 날짜 정보를 찾지 못했습니다.")
                    self.driver.back()
                    continue

                date_str_full = date_info_element.text.strip().replace("입력 ", "")
                article_date = datetime.strptime(date_str_full, "%Y.%m.%d %H:%M")

                if datetime.now() - article_date <= timedelta(days=7):
                    formatted_date = article_date.strftime('%Y-%m-%d')
                    print(f"-> 날짜 확인: {formatted_date} (수집 대상)")
                    
                    title = article_soup.select_one("h3.heading").text.strip()
                    
                    content_container = article_soup.select_one("article#article-view-content-div")
                    if content_container:
                        p_tags = content_container.find_all("p")
                        content = "\n".join([p.get_text(strip=True) for p in p_tags])
                    else:
                        content = "본문 내용을 찾을 수 없습니다."
                    
                    final_results.append({
                        "title": title,
                        "url": self.driver.current_url,
                        "content": content,
                        "date": formatted_date,
                        "source": "인공지능 신문",
                        "category": "기술"
                    })
                else:
                    formatted_date = article_date.strftime('%Y-%m-%d')
                    print(f"-> 날짜 확인: {formatted_date} (7일 경과). 수집을 중단합니다.")
                    self.driver.back()
                    break
                
                self.driver.back()

            except StaleElementReferenceException:
                print("페이지 요소가 변경되어 건너뜁니다.")
                self.driver.get(list_url)
                continue
            except Exception as e:
                print(f"처리 중 오류 발생: {e}")
                self.driver.get(list_url)
                continue

        print(f"인공지능 신문 크롤링 완료! 총 {len(final_results)}개의 기사를 수집했습니다.")
        return final_results

    def search_with_perplexity(self, context: str = "AI") -> list:
        """
        Perplexity API를 사용하여 AI 동향 데이터 수집
        
        Args:
            context (str): 검색 컨텍스트 (arxiv 키워드와 동일)
            
        Returns:
            list: 수집된 AI 동향 데이터 리스트
        """
        print(f"\n=== Perplexity API를 통한 AI 동향 데이터 수집 시작 (컨텍스트: {context}) ===")
        
        if not self.perplexity_api_key:
            print("❌ Perplexity API 키가 설정되지 않았습니다.")
            return []
        
        # 현재 날짜 계산
        current_date = datetime.now()
        start_date = (current_date - timedelta(days=7)).strftime("%Y-%m-%d")
        end_date = current_date.strftime("%Y-%m-%d")
        
        # 프롬프트 템플릿
        prompt_template = f"""
# 최종 목표 (Primary Goal)
당신의 유일한 임무는 아래에 명시된 구조와 규칙을 완벽하게 따르는 단일 JSON 객체를 생성하는 것입니다. JSON 객체 외에 어떠한 설명, 인사, 추가 텍스트도 출력해서는 안 됩니다.

# JSON 구조 및 규칙 (JSON Structure & Rules)
[
    {{
        "title": "주간 AI 기술 동향 보고서 ({start_date} ~ {end_date})",
        "url": "",
        "content": "{{CONTENT_PLACEHOLDER}}",
        "date": "{current_date.strftime('%Y-%m-%d')}",
        "source": "퍼플렉시티",
        "category": "종합"
    }}
]

# 'content' 필드 작성 지침 ({{CONTENT_PLACEHOLDER}}를 채우기 위한 규칙)
1.  **핵심 주제**: {start_date}부터 {end_date}까지, 지난 7일간 발생한 AI 분야 동향 중에서 **"{context}"와 직접적으로 관련된 내용을 최우선으로 다루어야 합니다.** "{context}" 관련 뉴스, 연구, 기술 발전, 기업 발표 등을 전체 내용의 70% 이상을 차지하도록 구성하세요.

2.  **분량**: 전체 글의 길이는 한국어 기준 1000자 내외로 맞춰주세요.

3.  **형식**: 여러 주제를 자연스럽게 엮어낸 줄글(prose) 형태로 작성합니다. 마크다운 헤더(#)나 글머리 기호(-)를 사용하지 마세요.

4.  **출처**: 신뢰도 높은 최신 기사, 논문, 발표 등을 바탕으로 내용을 구성하되, **매우 중요: 'content' 본문 안에는 절대로 URL, 웹사이트 이름, 논문 제목 등 출처를 표기하지 마세요.** 모든 정보를 자신의 분석인 것처럼 종합해서 서술해야 합니다.

5.  **컨텍스트 집중**: 
    - "{context}"와 직접 관련된 AI 기술, 연구, 기업 활동을 우선적으로 포함
    - "{context}" 관련 최신 동향과 발전 상황을 상세히 다루기
    - "{context}"가 AI 생태계에 미치는 영향과 의미를 분석
    - "{context}" 관련 기업들의 전략적 움직임과 투자 동향 포함
    - "{context}" 기술의 실제 적용 사례와 성과 다루기

6.  **보조 내용**: 나머지 30%는 "{context}"와 간접적으로 관련된 전체적인 AI 동향을 포함하되, 가능한 한 "{context}"와의 연관성을 찾아 연결하여 서술하세요.

7.  **구체성**: "{context}" 관련 내용은 구체적인 기술명, 기업명, 연구 결과, 수치 등을 포함하여 신뢰성 있는 정보를 제공하세요.
"""
        
        collected_data = []
        
        # 첫 번째 API 호출: 컨텍스트 중심 AI 동향
        print("1️⃣ 첫 번째 API 호출: 컨텍스트 중심 AI 동향 수집 중...")
        try:
            general_data = self._call_perplexity_api(prompt_template, f"{context} AI 기술 동향 최신 뉴스 연구 발전")
            if general_data:
                collected_data.extend(general_data)
                print("✅ 첫 번째 API 호출 완료")
        except Exception as e:
            print(f"❌ 첫 번째 API 호출 실패: {e}")
        
        # 두 번째 API 호출: 컨텍스트 특화 동향
        print("2️⃣ 두 번째 API 호출: 컨텍스트 특화 동향 수집 중...")
        try:
            context_data = self._call_perplexity_api(prompt_template, f"{context} 인공지능 기술 발전 기업 투자 연구 동향 최신 소식")
            if context_data:
                collected_data.extend(context_data)
                print("✅ 두 번째 API 호출 완료")
        except Exception as e:
            print(f"❌ 두 번째 API 호출 실패: {e}")
        
        print(f"Perplexity API 데이터 수집 완료! 총 {len(collected_data)}개의 데이터를 수집했습니다.")
        return collected_data
    
    def _call_perplexity_api(self, prompt_template: str, search_query: str) -> list:
        """
        Perplexity API 호출
        
        Args:
            prompt_template (str): 프롬프트 템플릿
            search_query (str): 검색 쿼리
            
        Returns:
            list: 파싱된 데이터 리스트
        """
        try:
            url = "https://api.perplexity.ai/chat/completions"
            
            headers = {
                "Authorization": f"Bearer {self.perplexity_api_key}",
                "Content-Type": "application/json"
            }
            
            # 프롬프트에 검색 쿼리 추가
            full_prompt = f"{prompt_template}\n\n**검색 주제**: {search_query}"
            
            payload = {
                "model": "sonar",
                "messages": [
                    {"role": "user", "content": full_prompt}
                ]
            }
            
            print(f"🔍 API 호출 중: {search_query[:50]}...")
            response = requests.post(url, json=payload, headers=headers, timeout=60)
            response.raise_for_status()
            
            data = response.json()
            content = data['choices'][0]['message']['content']
            
            # JSON 파싱
            parsed_data = self._parse_perplexity_response(content)
            return parsed_data if parsed_data else []
            
        except requests.exceptions.HTTPError as err:
            print(f"❌ Perplexity API HTTP 에러: {err} (상태 코드: {response.status_code})")
            print(f"응답 내용: {response.text}")
            return []
        except requests.exceptions.Timeout:
            print("❌ Perplexity API 호출 시간 초과 (60초)")
            return []
        except requests.exceptions.RequestException as e:
            print(f"❌ Perplexity API 호출 오류: {str(e)}")
            return []
        except Exception as e:
            print(f"❌ Perplexity API 호출 중 예상치 못한 오류: {str(e)}")
            return []
    
    def _parse_perplexity_response(self, response_text: str) -> list:
        """
        Perplexity API 응답을 파싱하여 데이터 추출
        
        Args:
            response_text (str): API 응답 텍스트
            
        Returns:
            list: 파싱된 데이터 리스트
        """
        try:
            # JSON 응답 추출
            if '[' in response_text and ']' in response_text:
                start = response_text.find('[')
                end = response_text.rfind(']') + 1
                json_str = response_text[start:end]
                parsed_data = json.loads(json_str)
                
                if isinstance(parsed_data, list):
                    return parsed_data
                elif isinstance(parsed_data, dict):
                    return [parsed_data]
                else:
                    return []
            else:
                print("⚠️ JSON 형식의 응답을 찾을 수 없습니다.")
                return []
                
        except json.JSONDecodeError as e:
            print(f"⚠️ JSON 파싱 오류: {e}")
            print(f"응답 텍스트: {response_text[:200]}...")
            return []
        except Exception as e:
            print(f"⚠️ 응답 파싱 중 예상치 못한 오류: {e}")
            return []

    def crawl_all_sources(self, arxiv_keyword="AI"):
        """모든 소스에서 크롤링 실행"""
        print("="*60)
        print("모든 소스에서 크롤링을 시작합니다...")
        print("="*60)
        
        all_results = []
        
        try:
            # Perplexity API를 통한 AI 동향 데이터 수집
            perplexity_data = self.search_with_perplexity(arxiv_keyword)
            all_results.extend(perplexity_data)
            
            # 파이토치 한국 사용자 모임
            pytorch_data = self.crawl_pytorch_kr()
            all_results.extend(pytorch_data)
            
            # TechCrunch
            techcrunch_data = self.crawl_techcrunch()
            all_results.extend(techcrunch_data)
            
            # HuggingFace Trending
            huggingface_data = self.crawl_huggingface()
            all_results.extend(huggingface_data)
            
            # AI타임즈
            aitimes_data = self.crawl_aitimes()
            all_results.extend(aitimes_data)
            
            # arXiv
            arxiv_data = self.crawl_arxiv(arxiv_keyword)
            all_results.extend(arxiv_data)
            
            # 인공지능 신문
            aitimes_kr_data = self.crawl_aitimes_kr()
            all_results.extend(aitimes_kr_data)
            
        except Exception as e:
            print(f"크롤링 중 오류가 발생했습니다: {e}")
        finally:
            self.close_driver()
        
        return all_results

    def save_results(self, data, filename="combined_search_results.json"):
        """결과를 JSON 파일로 저장"""
        with open(filename, "w", encoding="utf-8") as f:
            json.dump(data, f, ensure_ascii=False, indent=4)
        
        print(f"\n" + "="*60)
        print(f"크롤링 완료! 총 {len(data)}개의 데이터를 '{filename}' 파일에 저장했습니다.")
        print("="*60)
        
        # 카테고리별 통계 출력
        categories = {}
        sources = {}
        for item in data:
            cat = item.get('category', 'Unknown')
            src = item.get('source', 'Unknown')
            categories[cat] = categories.get(cat, 0) + 1
            sources[src] = sources.get(src, 0) + 1
        
        print("\n📊 카테고리별 통계:")
        for cat, count in categories.items():
            print(f"  {cat}: {count}개")
        
        print("\n📊 소스별 통계:")
        for src, count in sources.items():
            print(f"  {src}: {count}개")
        
        # Perplexity 데이터가 있는지 확인
        perplexity_count = sum(1 for item in data if item.get('source') == '퍼플렉시티')
        if perplexity_count > 0:
            print(f"\n🤖 Perplexity API 데이터: {perplexity_count}개")

class SearcherAgent(BaseAgent):
    """웹 크롤링 및 정보 수집 에이전트"""
    
    def __init__(self, perplexity_api_key: str = None):
        super().__init__(
            name="searcher",
            description="웹 크롤링 및 정보 수집 에이전트"
        )
        self.required_inputs = ["query", "arxiv_keyword"]
        self.output_keys = ["search_results", "search_metadata"]
        self.web_searcher = WebSearcher(perplexity_api_key)
    
    async def process(self, state: WorkflowState) -> WorkflowState:
        """웹 크롤링 및 정보 수집을 수행합니다."""
        self.log_execution("웹 크롤링 및 정보 수집 시작")
        
        try:
            # 입력 검증
            if not self.validate_inputs(state):
                raise ValueError("필수 입력이 누락되었습니다.")
            
            # 크롤링 실행
            arxiv_keyword = getattr(state, 'arxiv_keyword', 'AI')
            search_results = self.web_searcher.crawl_all_sources(arxiv_keyword)
            
            # 결과 저장
            output_filename = f"agent-cast/output/searcher/search_results_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
            self.web_searcher.save_results(search_results, output_filename)
            
            # 워크플로우 상태 업데이트
            new_state = WorkflowState(
                **{k: v for k, v in state.__dict__.items()},
                search_results=search_results,
                search_metadata={
                    "total_items": len(search_results),
                    "sources": list(set(item.get('source', 'Unknown') for item in search_results)),
                    "categories": list(set(item.get('category', 'Unknown') for item in search_results)),
                    "output_file": output_filename
                }
            )
            
            # 워크플로우 상태 업데이트
            new_state = self.update_workflow_status(new_state, "searcher_completed")
            
            self.log_execution(f"웹 크롤링 완료: {len(search_results)}개 항목 수집")
            return new_state
            
        except Exception as e:
            self.log_execution(f"웹 크롤링 중 오류 발생: {str(e)}", "ERROR")
            raise

def main():
    """메인 실행 함수"""
    # Perplexity API 키 입력 (선택사항)
    perplexity_api_key = input("Perplexity API 키를 입력하세요 (기본값 사용시 엔터): ").strip()
    if not perplexity_api_key:
        perplexity_api_key = None
    
    searcher = WebSearcher(perplexity_api_key=perplexity_api_key)
    
    # arXiv 검색 키워드 입력 (기본값: "AI")
    arxiv_keyword = input("arXiv 검색 키워드를 입력하세요 (기본값: AI): ").strip()
    if not arxiv_keyword:
        arxiv_keyword = "AI"
    
    # 모든 소스에서 크롤링 실행
    results = searcher.crawl_all_sources(arxiv_keyword)
    
    # 결과 저장
    searcher.save_results(results)

if __name__ == "__main__":
    main()
