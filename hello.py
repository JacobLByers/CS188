import requests

def main():
    response = requests.api.get('https://api.coindesk.com/v1/bpi/currentprice.json')
    print(response.content)


if __name__ == "__main__":
    main()
