# Download files from alex dataset and the using the corrosponding dois download full papers. 
import pyalex
import os
import random
#from paperscraper.pdf import save_pdf
#pip install git+https://github.com/titipata/scipdf_parser

DOI_SAVE_PATH = "./data/doi_list.txt"
INTERSECT_ID_SAVE_PATH = "./data/intersect_list.txt"

def make_list_of_papers_authors():
    year = 2023
    paper_info_save_path = "./data/" + "paper_info_list_" + str(year) + ".txt"
    #works = pyalex.Works().sample(100, random.randint(0, 100_000_000)).filter( publication_year = 2021, has_oa_accepted_or_published_version = True, language = "en", **{"primary_location.source.type":"journal"}).get()
    #for work in works:
    #    print(work["primary_location"]["pdf_url"])
    # function to load the data
    document_info, prev_author_list = load_paper_dict_from_file(paper_info_save_path)
    author_list = list()
    # get the list of intersecting authors
    if os.path.isfile(INTERSECT_ID_SAVE_PATH):
            # open the file and load up the dict
        with open(INTERSECT_ID_SAVE_PATH, 'r') as file:
            for line in file:
                author_id = line.strip()
                author_list.append(author_id)
    else:
        print("NO intersect data found!!")
        return
    # go through the authors works
    author_count = 0
    for author in author_list:
        author_count += 1
        if author in prev_author_list:
            continue
        print(author_count, author)
        works = pyalex.Works().filter(**{"author.id": author}, publication_year = year, has_oa_accepted_or_published_version = True, language = "en", **{"primary_location.source.type":"journal"}).get()
        for work in works:
            key = work["doi"]
            if document_info.get(key) is None:
                document_info[work["doi"]] = True
                entry_list = list()
                #print(work["doi"])
                if work["primary_location"]["pdf_url"] is not None:
                    #print(work["primary_location"]["pdf_url"])
                    entry_list.append(work["primary_location"]["pdf_url"])
                    #document_info[work["doi"]].append(work["primary_location"]["pdf_url"])
                else:
                    #print("None")
                    entry_list.append("None")
                    #document_info[work["doi"]].append("None")
                if work["primary_location"]["source"] is not None:
                    #print(work["primary_location"]["source"]["display_name"])
                    entry_list.append(work["primary_location"]["source"]["display_name"])
                    #document_info[work["doi"]].append(work["primary_location"]["source"]["display_name"])
                else:
                    #print("None")
                    entry_list.append("None")
                    #document_info[work["doi"]].append("None")
                if len(work["authorships"][0]["countries"]) != 0:
                    #print(work["authorships"][0]["countries"][0])
                    entry_list.append(work["authorships"][0]["countries"][0])
                    #document_info[work["doi"]].append(work["authorships"][0]["countries"][0])
                else:
                    #print("None")
                    entry_list.append("None")
                    #document_info[work["doi"]].append("None")
                #print("\n")
                #print(work["doi"], work["primary_location"]["pdf_url"], work["primary_location"]["source"]["display_name"], work["authorships"][0]["countries"])
                # SAVE THE DATA (document info)
                entry = "{}\t{}\t{}\t{}\t{}\n".format(author, key, entry_list[0], entry_list[1], entry_list[2])
                #print(entry)
                with open(paper_info_save_path, "a", encoding="utf-8") as f:
                    f.write(entry)

    return

def load_paper_dict_from_file(path):
    paper_dict = dict()
    author_list = list()
    if os.path.isfile(path):
        # open the file and load up the dict
        with open(path, 'r', encoding="utf-8") as file:
            for line in file:
                line_array = line.strip().split("\t")
                author_list.append(line_array[0])
                if paper_dict.get(line_array[1]) is None:
                    paper_dict[line_array[1]] = True
    return paper_dict, author_list


# Run this until, no new authors are found
def find_intersecting_authors_2021_2023_2025():
    years_to_analyze = [2025, 2023, 2021]
    # load previous entries
    author_dict = load_dict_from_author_file(years_to_analyze)
    #print(pyalex.Works().filter(publication_year = year).select("authorships").count())
    # loop through years
    for year in years_to_analyze:
        year_index = int((year - 2021) / 2)
        random_seed_start = random.randint(0, 100_000_000)
        for seed in range(random_seed_start, random_seed_start + 20):
            # seed to get random sample of 10_000 (max value), select only authorships
            pages = pyalex.Works().sample(10_000, seed).filter(publication_year = year, has_oa_accepted_or_published_version = True, language = "en", **{"primary_location.source.type":"journal"}).select("authorships").paginate(method="page", per_page=200)
            page_number = 0
            for page in pages:
                page_number += 1
                print(year, seed, seed -  random_seed_start,  page_number, len(author_dict))
                for work in page:
                    # save in dict, update bool based on year
                    for author in work["authorships"]:
                        if author["author"]["id"] is not None:
                            key = author["author"]["id"].split("/")[-1]
                            if author_dict.get(key) is not None:
                                author_dict[key][year_index] = True
                            else:
                                author_dict[key] = [False, False, False]
                                author_dict[key][year_index] = True
                if page_number == 50:
                    break
            # intermediate save
            if seed % 10 == 0 and seed != 0:
                keys_save = list()
                for key in author_dict.keys():
                    if author_dict[key][year_index] == True:
                        keys_save.append(key + "\n")
                with open("./data/" + str(year) + ".txt", "w") as f:
                    f.writelines(keys_save)

    # analyze the dict
    count_2021 = 0
    count_2023 = 0
    count_2025 = 0
    count_intersect = 0
    keys_intersect = []
    for key in author_dict.keys():
        if author_dict[key][0] == True:
            count_2021 += 1
        if author_dict[key][1] == True:
            count_2023 += 1
        if author_dict[key][2] == True:
            count_2025 += 1
        if author_dict[key][0] and author_dict[key][1] and author_dict[key][2] == True:
            count_intersect += 1
            keys_intersect.append(key + "\n")
    print("2021: ", count_2021, " 2023: ", count_2023, " 2025: ", count_2025, " Intersect: ", count_intersect)
    with open(INTERSECT_ID_SAVE_PATH, "w") as f:
        f.writelines(keys_intersect)
    return

def load_dict_from_author_file(years_to_analyze):
    author_dict = dict()
    for year in years_to_analyze:
        year_index = int((year - 2021) / 2)
        file_path = "./data/" + str(year) + ".txt"
        if os.path.isfile(file_path):
            # open the file and load up the dict
             with open(file_path, 'r') as file:
                for line in file:
                    key = line.strip()
                    if author_dict.get(key) is not None:
                        author_dict[key][year_index] = True
                    else:
                        author_dict[key] = [False, False, False]
                        author_dict[key][year_index] = True
    return author_dict
# obsolete
def get_and_save_dois():
    # go through years 1980 to 2025
    for year in range(1980, 2026):
        print(year)
        doi_list = list()
        # loop using different seeds until we get the desired amount of data (dois)
        for seed in range(0, 3):
            pages = pyalex.Works().sample(10_000, seed=seed).filter(publication_year=year, is_oa=True).select("doi").paginate(method="page", per_page=200)
            for page in pages:
                for result in page:
                    print(result["doi"])
                    if result["doi"] != None:
                        doi_list.append(result["doi"] + "\n")
        with open(DOI_SAVE_PATH, "a") as f:
            f.write(str(year) + "\n")
            f.writelines(doi_list)
    return

def retrieve_pdf_from_doi(year):
    # go through the doi list and get the releavant doi for the year and make a list
    start = False
    year_doi_list = list()
    with open(DOI_SAVE_PATH, 'r') as file:
        for line in file:
            if line.strip() == str(year + 1):
                break
            if start == True:
                year_doi_list.append(line.strip())
            if line.strip() == str(year):
                start = True
    print(len(year_doi_list))
    # try to download the doi, if fail do nothing if success put the file in year folder and save it to success list
    for doi in year_doi_list:
        name = doi
        print(doi)
        out = "./data/" + str(year) + "/" + name.replace("/", "").replace(":", "") + ".pdf"
        paper_data = {'doi': doi}
        save_pdf(paper_data, filepath=out)
        print(out)
        #scihub_download("https://doi.org/10.1145/3375633", out=out, paper_type="doi")
        break
    return

def main():
    #get_and_save_dois()
    #work = pyalex.Works().filter(doi = "https://doi.org/10.1186/s12859-024-06020-0").get()
    #pages = pyalex.Authors().filter(id = "https://openalex.org/A5060528195").get()
    #count = 0
    #print(pages)
    #find_intersecting_authors_2021_2023_2025()
    make_list_of_papers_authors()
    #retrieve_pdf_from_doi(1983)
    return 0

if __name__ == "__main__":  
    main()