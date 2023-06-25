'''
Web Crawler
Utkarsh Pant : 22B0914

'''
#importing required libraries
import requests
from bs4 import BeautifulSoup
from urllib.parse import urlparse, urljoin
import os.path
import argparse
import sys
import time
import warnings
warnings.filterwarnings("ignore") #suppress warnings

#defining all the command line arguments
arg_parser = argparse.ArgumentParser()
arg_parser.add_argument("-u", "--url",nargs="+", help="Website link to crawl", required=True)
arg_parser.add_argument("-t", "--threshold", help="Threshold of recursion depth", const=None, type=int)
arg_parser.add_argument("-o", "--output", nargs="?", const=None, help="output file name")
arg_parser.add_argument("-c", "--count", help="Number of Each extension",action="store_true")
arg_parser.add_argument("-d", "--desegregate", help="Desegregates the links",action="store_true")
arg_parser.add_argument("-i", "--internal", help="prints only internal links",action="store_true")
arg_parser.add_argument("-T", "--time", help="prints execution time",action="store_true")
args = arg_parser.parse_args()

iurl = set(args.url)
threshold = args.threshold
output_file = args.output 

#error handling 
if not iurl:
    print("URL is required!", file=sys.stderr)
    sys.exit(1)

if threshold is not None:
    if threshold <= 0:
        print("Invalid threshold!", file=sys.stderr)
        sys.exit(1)

if output_file:
    with open(output_file, "w") as file:
        file.close()
    #Empties the output_file if it was non empty 


tags = ['a', 'link', 'script', 'img']#attributes to be checked for scraping

# Function to extract links from a URL into a set
def extract_links(url,links):

    try:
        response = requests.get(url)
        soup = BeautifulSoup(response.content, 'lxml')

        for tag in soup.find_all(tags):
        
            href = tag.get('href')
            if href:
                links.add(urljoin(url, href))
            src = tag.get('src')
            if src:
                links.add(urljoin(url, src))
    except requests.exceptions.RequestException:
        pass

#Function to segregate links based on their extensions into a dicrionary
def extension_segregator(url_set):
    try:
        ext_seg = {}
        for link in url_set:
            parsed_link = urlparse(link)

            path = parsed_link.path
            extension = os.path.splitext(path)[1]

            if extension in ext_seg.keys():
                ext_seg[extension].add(link)
            else:
                ext_seg[extension] = set()
                ext_seg[extension].add(link)

        return ext_seg

    except requests.exceptions.RequestException:
        pass

# Function to filter internal links based on command line URLs
def filter_internal_links(links, base_url = iurl):

    base_netloc= set()
    for base_link in base_url:
        base_netloc.add(urlparse(base_link).netloc)
    internal_links = set()

    for link in links:

        parsed_link = urlparse(link)
        if parsed_link.netloc in base_netloc:
            #compares net  location of links in input set and links 
            internal_links.add(link)
    return internal_links

# Function to print segregated links and their extensions
def seg_print(extracted_links,ext_seg):


    sorted_dict = sorted(ext_seg.items(), key = lambda x:-len(x[1]))#sorting by number of files per extension
    converted_dict = dict(sorted_dict)
    print("Total Links found:",len(extracted_links))
    
    for extension in converted_dict.keys():
        if extension == "":
            print("Miscellaneous : {}".format(len(converted_dict[extension])))
        elif extension == "Desgregate Links":
            pass
        else:
            print("{} : {}".format(extension,len(converted_dict[extension])))
        for url in converted_dict[extension]:
            print(url)
    print()

# Function to print link counts based on extensions
def c_print(links,ext_seg):
    sorted_dict = sorted(ext_seg.items(), key = lambda x:-len(x[1])) #sorting
    converted_dict = dict(sorted_dict)
    print("Total Links found:",len(links))
    for extension in converted_dict.keys():
        if extension == "":
            print("Miscellaneous : {}".format(len(converted_dict[extension])))
        elif extension == "Desgregate Links":
            continue
        else:
            print("{} : {}".format(extension,len(converted_dict[extension])))
    print()

# Function to recursively print links particular for infinite depth search
def print_links_recursive(url, visited_links):

    if url in visited_links:
        #base case
        return
    
    visited_links.add(url)
    links = set()
    extract_links(url, links)
    internal_links = filter_internal_links(links)
    visited_links.update(links - internal_links) #adding external links without iterating through them
    for link in internal_links:
        #iterating through all internal links
        print_links_recursive(link, visited_links)

# Function to crawl and analyze links
def crawl(url_set,depth,rec_lvl = 1):

    if depth == 0:
        #base case
        return
    
    links = set()
    for link in url_set:
        extract_links(link,links)
    if args.internal:
        links = filter_internal_links(links)
    if args.desegregate:
        ext_seg = {"Desgregate Links":links}
    else:
        ext_seg = extension_segregator(links)
    if output_file:
        with open(output_file, "a") as file:
            sys.stdout = file
            if args.count:
                print("At recursion level",rec_lvl)
                c_print(links,ext_seg)
            else:
                print("At recursion level",rec_lvl)
                seg_print(links,ext_seg)
            sys.stdout = sys.__stdout__
    else:
        if args.count:
            print("At recursion level",rec_lvl)
            c_print(links,ext_seg)
        else:
            print("At recursion level",rec_lvl)
            seg_print(links,ext_seg)

    new_urlset = filter_internal_links(links)
    crawl(new_urlset,depth-1,rec_lvl+1)


start = time.time()

if threshold is None:
    #infinite depth search

    links =set()

    for url in iurl:
        #iterating through all input urls
        print_links_recursive(url,links) 
    if args.internal:
        links = filter_internal_links(links)   
    if args.desegregate:
        ext_seg = {"Desgregate Links":links}
    else:
        ext_seg = extension_segregator(links)

    if output_file:
        with open(output_file, "a") as file:
            sys.stdout = file
            if args.count:
                print("At recursion level infinite")
                c_print(links,ext_seg)
            else:
                print("At recursion level infinite")
                seg_print(links,ext_seg)
            sys.stdout = sys.__stdout__
    else:

        if args.count:
            print("At recursion level infinite")
            c_print(links,ext_seg)
        else:
            print("At recursion level infinite")
            seg_print(links,ext_seg)

else:

    crawl(iurl,threshold)

end = time.time()

if args.time:
    print(f"Time taken: {(end-start)*1000:.03f} ms")