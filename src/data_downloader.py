# Download files from alex dataset and the using the corrosponding dois download full papers. 
import pyalex
import os
import random
import copy
#from paperscraper.pdf import save_pdf
#pip install git+https://github.com/titipata/scipdf_parser

DOI_SAVE_PATH = "./data/doi_list.txt"
INTERSECT_ID_SAVE_PATH = "./data/intersect_list.txt"
PAPER_INFO_SAVE_PATH = "./data/paper_info_list.txt"
PAPER_DOWNLOAD_SAVE_PATH = "./data/paper_download_list.txt"
AI_INFO_SAVE_PATH = "./data/ai_info_list.txt"
JOURNAL_FIELD_PATH = "./data/journal_list_with_fields.txt"
TOKEN_PATH = "./data/token.txt"

def display_all_required_info():
    #print(2021, "paper count: ", pyalex.Works().filter(publication_year = 2021, has_oa_accepted_or_published_version = True, language = "en", **{"primary_location.source.type":"journal"}).count())
    #print(2023, "paper count: ", pyalex.Works().filter(publication_year = 2023, has_oa_accepted_or_published_version = True, language = "en", **{"primary_location.source.type":"journal"}).count())
    #print(2025, "paper count: ", pyalex.Works().filter(publication_year = 2025, has_oa_accepted_or_published_version = True, language = "en", **{"primary_location.source.type":"journal"}).count())
    # load the journal fields
    fields = ["Life Sciences", "Physical Sciences", "Engineering & Technology", "Social Sciences", "Humanities", "Business & Economics", "Multidisciplinary"]
    stem_non_stem = [["Life Sciences", "Physical Sciences", "Engineering & Technology"], ["Social Sciences", "Humanities", "Business & Economics"]]
    journal_content_list = [[], [], [], [], [], [], []]
    with open(JOURNAL_FIELD_PATH, 'r', encoding="utf-8") as file:
        for line in file:
            line_array = line.strip().split(",")
            field = line_array[-1].strip()
            journal = line_array[0].strip()
            index = fields.index(field)
            journal_content_list[index].append(journal)
    # load the country regions
    country_content_list = [["DZ", "AO", "BJ", "BW", "BF", "BI", "CV", "CM", "CF", "TD", "KM", "CG", # Africa 
                    "CD", "CI", "DJ", "EG", "GQ", "ER", "SZ", "ET", "GA", "GM", "GH", "GN",
                    "GW", "KE", "LS", "LR", "LY", "MG", "MW", "ML", "MR", "MU", "MA", "MZ",
                    "NA", "NE", "NG", "RW", "ST", "SN", "SC", "SL", "SO", "ZA", "SS", "SD",
                    "TZ", "TG", "TN", "UG", "ZM", "ZW"],
                    ["CA", "US", "MX", "PR", "GL", "MQ"], # North_America 
                    ["BZ", "CR", "SV", "GT", "HN", "NI", "PA", "AG", "BS", "BB", "CU", "DM", "DO", "GD", "HT", "JM", "KN", "LC", "VC", "TT", "GP", "XK", "CW"], # Central_America/Caribbean
                    ["AR", "BO", "BR", "CL", "CO", "EC", "GY", "PY", "PE", "SR", "UY", "VE", "GF"], # South_America
                    ["AF", "AM", "AZ", "BH", "BD", "BT", "BN", "KH", "CN", "CY", "GE", "IN", "ID", "IR", "IQ", "IL", "JP", "JO", "KZ", "KW", 
                    "KG", "LA", "LB", "MY", "MV", "MN", "MM", "NP", "KP", "OM", "PK", "PH", "QA", "SA", "SG", "KR", "LK", "SY", "TW", "TJ", 
                    "TH", "TL", "TR", "TM", "AE", "UZ", "VN", "YE", "HK", "PS", "MO"], # Asia
                    ["AL", "AD", "AT", "BY", "BE", "BA", "BG", "HR", "CZ", "DK", "EE", "FI", "FR", "DE", "GR", "HU", "IS",  # Europe 
                    "IE", "IT", "LV", "LI", "LT", "LU", "MT", "MD", "MC", "ME", "NL", "MK", "NO", "PL", "PT", "RO", "RU", 
                    "SM", "RS", "SK", "SI", "ES", "SE", "CH", "UA", "GB", "VA", "XK", "GI"], 
                    ["AU", "FJ", "KI", "MH", "FM", "NR", "NZ", "PW", "PG", "WS", "SB", "TO", "TV", "VU", "MP", "PF", "NC"]] # Oceania
    ai_score_bin_empty = [[0] * 10, [0] * 10, [0] * 10]
    ai_score_bin = copy.deepcopy(ai_score_bin_empty)
    stem_region_ai_scores = [[copy.deepcopy(ai_score_bin_empty) for _ in range(7)], [copy.deepcopy(ai_score_bin_empty) for _ in range(7)]]
    country_ai_scores = [copy.deepcopy(ai_score_bin_empty) for _ in range(7)]
    journal_ai_scores = [copy.deepcopy(ai_score_bin_empty) for _ in range(7)]
    journal_dict = dict()
    author_dict = dict()
    year_counts = [0, 0, 0]
    ai_over_all_counts = [0] * 200
    non_ai_over_all_counts = [0] * 200
    paper_limit_for_year = 200_000
    no_country_count = 0
    no_journal_count = 0
    if os.path.isfile(AI_INFO_SAVE_PATH):
        # open the file and load up the dict
        with open(AI_INFO_SAVE_PATH, 'r', encoding="utf-8") as file:
            for line in file:
                line_array = line.strip().split("\t")
                year = int(line_array[5])
                year_index = int((year - 2021) / 2)
                year_counts[year_index] += 1
                if year_counts[year_index] > paper_limit_for_year:
                    continue
                ai_score = float(line_array[6].split(" ")[1]) * 10_000
                author = line_array[0]
                country = line_array[4]
                journal = line_array[3]
                if int(ai_score) > 9:
                    ai_score_bin[year_index][9] += 1
                else:
                    ai_score_bin[year_index][int(ai_score)] += 1
                if author_dict.get(author) is None:
                    author_dict[author] = True
                if journal_dict.get(journal) is None:
                    journal_dict[journal] = True
                # find the country index
                country_index = 0
                country_found = False
                journal_index = 0
                journal_found = False
                for index, country_list in enumerate(country_content_list):
                    if country in country_list:
                        country_index = index
                        country_found = True
                if country_found == False and country != "None":
                    print(country)
                # find the journal index 
                for index, journal_list in enumerate(journal_content_list):
                    if journal in journal_list:
                        journal_index = index
                        journal_found = True
                if country_found == False:
                    no_country_count += 1
                    continue
                if journal_found == False:
                    no_journal_count += 1
                    continue
                overall_index = (year_index * 7 * 7) + (journal_index * 7) + (country_index)
                if ai_score > 0.9:
                    ai_over_all_counts[overall_index] += 1
                elif ai_score < 0.1:
                    non_ai_over_all_counts[overall_index] += 1
                #print(overall_index)
                # if int(ai_score) > 9:
                #     if country_found == True:
                #         country_ai_scores[country_index][year_index][9] += 1
                #     journal_ai_scores[journal_index][year_index][9] += 1
                # else:
                #     if country_found == True:
                #         country_ai_scores[country_index][year_index][int(ai_score)] += 1
                #     journal_ai_scores[journal_index][year_index][int(ai_score)] += 1
                # if country_found == True:
                #     if journal_index > 2 and journal_index != 6:
                #         if int(ai_score) > 9:
                #             stem_region_ai_scores[1][country_index][year_index][9] += 1
                #         else:
                #             stem_region_ai_scores[1][country_index][year_index][int(ai_score)] += 1
                #     elif journal_index != 6:
                #         if int(ai_score) > 9:
                #             stem_region_ai_scores[0][country_index][year_index][9] += 1
                #         else:
                #             stem_region_ai_scores[0][country_index][year_index][int(ai_score)] += 1
    print(no_journal_count)
    print(no_country_count)
    print("Overall")
    print(ai_score_bin[0])
    print(ai_score_bin[1])
    print(ai_score_bin[2])
    print(len(author_dict))
    # print("Region")
    # for country_score in country_ai_scores:
    #     print(country_score)
    # print("Field") 
    # for journal_score in journal_ai_scores:
    #     print(journal_score)
    # print("STEM NON STEM")
    # for stem_array in stem_region_ai_scores:
    #     print("Stem/NonStem")
    #     for region_score in stem_array:
    #         print(region_score)
    with open("./data/overall_ai_non_ai.txt", "a", encoding="utf-8") as f:
        for index, (ai, non_ai) in enumerate(zip(ai_over_all_counts, non_ai_over_all_counts)):
            print(index, ai, non_ai)
            f.write(str(index) + "," + str(ai) + "," + str(non_ai) + "\n")
    return


def retrieve_pdf_from_list_of_papers():
    document_info, _ = load_paper_dict_from_file(PAPER_INFO_SAVE_PATH, True)
    saved_document_info, _ = load_paper_dict_from_file(PAPER_DOWNLOAD_SAVE_PATH, False)
    paper_index = 0
    skip_one = True
    for document_key in document_info.keys():
        if saved_document_info.get(document_key) is None:
            if skip_one == True:
                skip_one = False
                continue
            array = document_info[document_key].split("\t")
            doi = array[1]
            paper_data = {'doi': doi[16:]}
            file_path_pdf = "./data/papers/" + str(paper_index) + ".pdf"
            file_path_xml = "./data/papers/" + str(paper_index) + ".xml"
            # try to obtain using the doi
            save_pdf(paper_data, filepath=file_path_pdf, api_keys=TOKEN_PATH)
            # check if file exists, if does not put fail, otherwise put file path
            if os.path.isfile(file_path_pdf):
                file_path = file_path_pdf
            elif os.path.isfile(file_path_xml):
                file_path = file_path_xml
            else:
                file_path = "fail"
            with open(PAPER_DOWNLOAD_SAVE_PATH, "a", encoding="utf-8") as f:
                f.write(document_info[document_key] + "\t" + file_path + "\n")
        paper_index += 1
    return

def make_list_of_papers_authors():
    document_info, final_author = load_paper_dict_from_file(PAPER_INFO_SAVE_PATH, False)
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
    skip_stop = False
    for author in author_list:
        author_count += 1
        if (author == final_author) or (final_author == None):
            skip_stop = True
        if skip_stop == False:
            continue
        print(author_count, author)
        works = pyalex.Works().filter_or(**{"author.id": author}, publication_year = [2021, 2023, 2025], has_oa_accepted_or_published_version = True, language = "en", **{"primary_location.source.type":"journal"}).get()
        for work in works:
            key = work["doi"]
            if document_info.get(key) is None:
                document_info[work["doi"]] = True
                entry_list = list()
                if work["primary_location"]["pdf_url"] is not None:
                    entry_list.append(work["primary_location"]["pdf_url"])
                else:
                    entry_list.append("None")

                if work["primary_location"]["source"] is not None:
                    entry_list.append(work["primary_location"]["source"]["display_name"])
                else:
                    entry_list.append("None")
                if len(work["authorships"][0]["countries"]) != 0:
                    entry_list.append(work["authorships"][0]["countries"][0])
                else:
                    entry_list.append("None")
                entry_list.append(work["publication_year"])
                # SAVE THE DATA (document info)
                entry = "{}\t{}\t{}\t{}\t{}\t{}\n".format(author, key, entry_list[0], entry_list[1], entry_list[2], entry_list[3])
                with open(PAPER_INFO_SAVE_PATH, "a", encoding="utf-8") as f:
                    f.write(entry)
    return

def load_paper_dict_from_file(path, all_info):
    paper_dict = dict()
    final_author = None
    if os.path.isfile(path):
        # open the file and load up the dict
        with open(path, 'r', encoding="utf-8") as file:
            for line in file:
                line_array = line.strip().split("\t")
                final_author = line_array[0]
                if paper_dict.get(line_array[1]) is None:
                    if all_info == True:
                        paper_dict[line_array[1]] = line.strip()
                    else:
                        paper_dict[line_array[1]] = True
    print(final_author)
    return paper_dict, final_author


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

def main():
    #find_intersecting_authors_2021_2023_2025()
    #make_list_of_papers_authors()
    #retrieve_pdf_from_list_of_papers()
    display_all_required_info()
    return 0

if __name__ == "__main__":  
    main()