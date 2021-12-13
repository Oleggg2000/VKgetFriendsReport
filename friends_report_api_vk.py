import sys
import logging

import requests
from json import dump

from config import ACCESS_TOKEN, USER_ID

CSV_TSV_PAGINATION_NUM = 65536  # Equal to limit of CSV rows in Open Office program (250000 rows for MS Excel)
JSON_PAGINATION_NUM = 65536

# Logging implementation
logger = logging.getLogger("api_key.py")
logger.setLevel(logging.INFO)
file_handler = logging.FileHandler("logs.log")
formatter = logging.Formatter("%(asctime)s - %(name)s - %(levelname)s - %(message)s")
file_handler.setFormatter(formatter)
logger.addHandler(file_handler)


def json_report(res_, path_):
    logger.info("Entered to json_report function")
    queue = ["first_name", "last_name", "country", "city", "bdate", "sex"]
    count, count_file, file_num = 0, 1, ""
    data = res_.json()
    report = {"people": []}
    person_dict = dict()
    for person in data["response"]["items"]:
        for queue_key in queue:
            for key in person:
                if queue_key == key and (key == "country" or key == "city"):
                    person_dict[key] = person[key]["title"]
                    break
                elif queue_key == key == "bdate":
                    temp = person[key].split(".")
                    if len(temp) == 2:
                        person_dict[key] = f"{temp[1]}-{temp[0]}"
                        break
                    else:
                        person_dict[key] = f"{temp[2]}-{temp[1]}-{temp[0]}"
                        break
                elif queue_key == key:
                    person_dict[key] = person[key]
                    break
        report["people"].append(person_dict)
        person_dict = dict()
        if sys.getsizeof(report) > 5368708121:  # 5,368,709,121 bytes (5 GB) JSON parser limits according to ibm.com
            logger.error("Size of JSON file is too big! Exiting from json_report function")
            print("Size of JSON file is too big! Interrupting...")  # Реализовать логирование
            return

        # Pagination implementation
        count += 1
        if count % JSON_PAGINATION_NUM == 0 and len(data["response"]["items"]) != count:
            with open(f"{path_}{file_num}.json", "w") as f:
                dump(report, f, indent=4)
            logging.info(f"{path_}{file_num}.json was saved and closed")
            report = {"people": []}
            file_num = str(count_file)
            count_file += 1
    with open(f"{path_}{file_num}.json", "w") as f:
        dump(report, f, indent=4)
    logging.info(f"{path_}{file_num}.json was saved and closed")
    logger.info("Exited from json_report function")


def csv_tsv_reports(res_, format_, path_):
    logger.info("Entered to csv_tsv_report function")
    queue = ["first_name", "last_name", "country", "city", "bdate", "sex"]
    count, count_file, file_num = 0, 1, ""
    f = open(f'{path_}{file_num}.{format_}', "w", encoding="utf-8")
    data = res_.json()
    for person in data["response"]["items"]:
        for queue_key in queue:
            for key in person:
                if queue_key == key and (key == "country" or key == "city"):
                    if format_ == "csv":
                        f.write(person[key]["title"] + ",")
                        break
                    else:
                        f.write(person[key]["title"] + "\t")
                        break
                elif queue_key == key == "bdate":
                    temp = person[key].split(".")
                    if len(temp) == 2:
                        if format_ == "csv":
                            f.write(f"{temp[1]}-{temp[0]},")
                            break
                        else:
                            f.write(f"{temp[1]}-{temp[0]}\t")
                            break
                    else:
                        if format_ == "csv":
                            f.write(f"{temp[2]}-{temp[1]}-{temp[0]},")
                            break
                        else:
                            f.write(f"{temp[2]}-{temp[1]}-{temp[0]}\t")
                            break
                elif queue_key == key == "sex":
                    f.write(str(person[key]))
                    break
                elif queue_key == key:
                    if format_ == "csv":
                        f.write(person[key] + ",")
                        break
                    else:
                        f.write(person[key] + "\t")
                        break
            if format_ == "csv":
                f.write(",")
            else:
                f.write("\t")
        f.write("\n")

        # Pagination implementation
        count += 1
        if count % CSV_TSV_PAGINATION_NUM == 0 and len(data["response"]["items"]) != count:
            file_num = str(count_file)
            f.close()
            logging.info(f"{path_}{file_num}.{format_} was saved and closed")
            f = open(f'{path_}{file_num}.{format_}', "w", encoding="utf-8")
            count_file += 1
            logging.info(f"{path_}{file_num}.{format_} was created")
    f.close()
    logger.info("Exited from csv_tsv_report function")


def friends_report(access_token, user_id, outcomes_format="csv", outcomes_path="report"):
    logger.info("Entered to the friends_report function")
    response = requests.get(("https://api.vk.com/method/friends.get?v=5.131&fields=country,city,bdate,sex&"
                            f"order=name&access_token={access_token}&user_id={user_id}"))
    try:
        if response.json()["error"]:
            logger.error(f'HTTP error occurred: {response.json()["error"]["error_msg"]}')
            print(f'HTTP error occurred: {response.json()["error"]["error_msg"]}')
            return
    except KeyError:
        pass

    try:
        if outcomes_format.lower() == "csv" or outcomes_format.lower() == "tsv":
            csv_tsv_reports(response, outcomes_format.lower(), outcomes_path)
        elif outcomes_format.lower() == "json":
            json_report(response, outcomes_path)
        else:
            logger.error("The entered format isn't supported! Try one of these: csv, json or tcs")
            print("The entered format isn't supported! Try one of these: csv, json or tcs")
    except FileNotFoundError as error_pass:
        logger.error(f"Directory {error_pass.filename} doesn't exist!")
        print(f"Directory {error_pass.filename} doesn't exist!")
    logger.info("Exited from friends_report function")


if __name__ == "__main__":
    logger.info("Program started!")
    if len(sys.argv) == 3:
        logger.info("Three arguments were submitted for input")
        friends_report(access_token=ACCESS_TOKEN, user_id=USER_ID,
                       outcomes_format=sys.argv[1], outcomes_path=sys.argv[2])
    elif input(("Do you want to type in output format of the file and path to output file?\n"
                "If not then default format and path will apply. y/n: ")) == "y":
        logger.info("Less or more than three arguments were submitted for input")
        logger.info("Arguments were typed in from keyboard")
        friends_report(access_token=ACCESS_TOKEN, user_id=USER_ID,
                       outcomes_format=input("Type in format of output file: "),
                       outcomes_path=input("Type in path to the output file and it's name: "))
    else:
        logger.info("Running program with default arguments")
        friends_report(access_token=ACCESS_TOKEN, user_id=USER_ID)
    logger.info("The program is completed! ")
    logger.info("---------------------------------------------------------------------")
