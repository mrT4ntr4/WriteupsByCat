import requests,time
from bs4 import BeautifulSoup
from halo import Halo
from tabulate import tabulate
from collections import OrderedDict
import argparse

def filterScrape(need, category, page):

	spinner = Halo(text='Scraping content', spinner='dots',animation='bounce')
	headers = {'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_10_1) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/39.0.2171.95 Safari/537.36'}
	output_dic = OrderedDict()
	found=0

	try:	
		while(found < need):
			spinner.start()
			url = "https://ctftime.org/writeups?page={}&hidden-tags={}".format(page,category)
			spinner.text = "Scraping Page: {}".format(page)
			response = requests.get(url, headers=headers)
			soup = BeautifulSoup(response.content, 'html.parser')
			count_per_page = 0
			for tr in soup.find_all('tr')[1:]:
				tds = tr.find_all('td')
				w_no = tds[4].a["href"]
				task_name = tds[1].text
				writeup_url = "https://ctftime.org/"+w_no
				r = requests.get(writeup_url, headers=headers)
				spinner.text = "Parsing {} ({})".format(w_no,task_name.encode('ascii', 'ignore').decode('ascii'))
				spinner.color = "red"
				
				if(len(task_name)>30):
					task_name = task_name[:27]+'...'

				flag = 0
				original_url = ""
				new_soup =  BeautifulSoup(r.content, 'lxml')
				a = new_soup.find_all('a')

				for link in a:
					if link.text == "Original writeup":
						original_url = link['href']
						if(len(original_url)<=125):
							flag = 1
							break
				if flag == 1:
					if(task_name in output_dic):
						output_dic[task_name]+='\n'+original_url
					else:
						output_dic[task_name]=original_url
						count_per_page+=1
						found+=1
				else:
					if task_name not in output_dic:
						count_per_page+=1
						found+=1
					output_dic[task_name] = writeup_url


				if(found == need):
					break
				else:
					continue

			if(count_per_page == 0):
				spinner.fail("Page {} doesn't exist.".format(page))
				spinner.info("Try decreasing the Page Seed or limit")
				spinner.info("Try changing the category")
				print("Such as : Change 'rev' -> 'reverse engineering' to get more results")
				break
			else:
				spinner.succeed("Gathered writeups for {} tasks from page {}".format(count_per_page,page))
				spinner.color = "cyan"
				page+=1

		return output_dic

	except (KeyboardInterrupt, SystemExit):
		spinner.warn('Program exited unexpectedly')
		exit()
		

def printTable(dic_to_print):
	title = ["Task", "Writeup URL"]
	table = [(v,k) for v,k in dic_to_print.items()]

	print(tabulate(table, headers=title, tablefmt="fancy_grid", showindex = True))

if __name__ == "__main__":
	parser = argparse.ArgumentParser(description="Read writeups for your favourite category")

	parser.add_argument("-c", "--category", help="specify the category to filter writeups (In quotes)", type=str, required=True)
	parser.add_argument("-l", "--limit", help="limit the number of tasks (Default = 10)", type=int, default=10)
	parser.add_argument("-p", "--page", help="seed for the page number (Default = 1)", type=int, default=1)
	args = parser.parse_args()

	category = args.category.strip('"\'')
	limit = args.limit
	page = args.page

	print("Filtering Category : \033[1;32;40m%s" % category)
	print("Limit : \033[1;32;40m%s" % limit)

	dic_to_print = filterScrape(limit,category,page)

	if(len(dic_to_print) != 0):
		printTable(dic_to_print)