import requests
from json import dump

from config import ACCESS_TOKEN, USER_ID


def json_report(res_, path_):
    queue = ["first_name", "last_name", "country", "city", "bdate", "sex"]
    data = res_.json()
    report = {"people": []}
    person_dict = dict()
    for person in data["response"]["items"]:
        for queue_key in queue:
            for key in person:
                if queue_key == key and (key == "country" or key == "city"):
                    person_dict[key] = person[key]["title"]
                elif queue_key == key == "bdate":
                    temp = person[key].split(".")
                    if len(temp) == 2:
                        person_dict[key] = f"{temp[1]}-{temp[0]}"
                    else:
                        person_dict[key] = f"{temp[2]}-{temp[1]}-{temp[0]}"
                elif queue_key == key:
                    person_dict[key] = person[key]
        report["people"].append(person_dict)
        person_dict = dict()

    with open(f"{path_}.json", "w") as f:
        dump(report, f, indent=4)


def csv_tsv_reports(res_, format_, path_):

    with open(f'{path_}.{format_}', "w+", encoding="utf-8") as f:
        queue = ["first_name", "last_name", "country", "city", "bdate", "sex"]
        data = res_.json()
        for person in data["response"]["items"]:
            for queue_key in queue:
                for key in person:
                    if queue_key == key and (key == "country" or key == "city"):
                        if format_ == "csv":
                            f.write(person[key]["title"] + ",")
                        else:
                            f.write(person[key]["title"] + "\t")
                    elif queue_key == key == "bdate":
                        temp = person[key].split(".")
                        if len(temp) == 2:
                            if format_ == "csv":
                                f.write(f"{temp[1]}-{temp[0]},")
                            else:
                                f.write(f"{temp[1]}-{temp[0]}\t")
                        else:
                            if format_ == "csv":
                                f.write(f"{temp[2]}-{temp[1]}-{temp[0]},")
                            else:
                                f.write(f"{temp[2]}-{temp[1]}-{temp[0]}\t")
                    elif queue_key == key == "sex":
                        f.write(str(person[key]))
                    elif queue_key == key:
                        if format_ == "csv":
                            f.write(person[key] + ",")
                        else:
                            f.write(person[key] + "\t")
            f.write("\n")


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


friends_report(access_token=ACCESS_TOKEN, user_id=USER_ID, outcomes_format="TCS", outcomes_path="reports/report")