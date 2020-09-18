from main import main

if __name__ == '__main__':
    client_id = ""
    client_secret = ""
    result = main(client_id, client_secret, only_profitable=True, request_per_minute_olx=120)

    print(result)
