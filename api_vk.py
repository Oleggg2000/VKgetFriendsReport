import sys

import requests
from json import dump

from config import ACCESS_TOKEN, USER_ID

CSV_TSV_PAGINATION_NUM = 65536  # Equal to limit of CSV rows in Open Office program (250000 rows for MS Excel)
JSON_PAGINATION_NUM = 65536


def json_report(res_, path_):
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
            print("Size of JSON file is too big! Interrupting...")  # Реализовать логирование
            return

        # Реализация пагинации
        count += 1
        if count % JSON_PAGINATION_NUM == 0 and len(data["response"]["items"]) != count:
            with open(f"{path_}{file_num}.json", "w") as f:
                dump(report, f, indent=4)
            report = {"people": []}
            file_num = str(count_file)
            count_file += 1
    with open(f"{path_}{file_num}.json", "w") as f:
        dump(report, f, indent=4)


def csv_tsv_reports(res_, format_, path_):
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
        f.write("\n")

        # Реализация пагинации
        count += 1
        if count % CSV_PAGINATION_NUM == 0 and len(data["response"]["items"]) != count:
            file_num = str(count_file)
            f.close()
            f = open(f'{path_}{file_num}.{format_}', "w", encoding="utf-8")
            count_file += 1
    f.close()


def friends_report(access_token, user_id, outcomes_format="csv", outcomes_path="report"):
    response = requests.get(("https://api.vk.com/method/friends.get?v=5.131&fields=country, city, bdate, sex&"
                            f"order=name&access_token={access_token}&user_id={user_id}"))
    try:
        if response.json()["error"]:
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
            print("The entered format isn't supported! Try one of these: csv, json or tcs")
    except FileNotFoundError as error_pass:
        print(f"Directory {error_pass.filename} doesn't exist!")


if __name__ == "__main__":
    if len(sys.argv) == 3:
        friends_report(access_token=ACCESS_TOKEN, user_id=USER_ID, outcomes_format=sys.argv[1], outcomes_path=sys.argv[2])
    elif input(("Do you want to type in output format of the file and path to output file?\n"
                "If not then default format and path will apply. y/n: ")) == "y":
        friends_report(access_token=ACCESS_TOKEN, user_id=USER_ID,
                       outcomes_format=input("Type in format of output file: "),
                       outcomes_path=input("Type in path to the output file and it's name: "))
    else:
        friends_report(access_token=ACCESS_TOKEN, user_id=USER_ID)
