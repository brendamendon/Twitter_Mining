from bs4 import BeautifulSoup
from csv import DictWriter
import pickle
from selenium import webdriver
from selenium.webdriver.support.ui import WebDriverWait
import time


def init_driver(driver_type):
    # Define qual driver será utilizado
    if driver_type == 1:
        driver = webdriver.Firefox()
    elif driver_type == 2:
        driver = webdriver.Chrome()
    elif driver_type == 3:
        driver = webdriver.Ie()
    elif driver_type == 4:
        driver = webdriver.Opera()
    elif driver_type == 5:
        driver = webdriver.PhantomJS()
    
    # Aguardando 5 segundos para continuar a execução do código
    driver.wait = WebDriverWait(driver, 5)

    return driver

def abre_html(driver, page):
    # Abre a página
    driver.get(page)
    
    return driver

def aplica_cookies(driver, dir):
    try:
        # Carrega os cookies
        cookies = pickle.load(open(fr'{dir}\cookies.pkl', "rb"))

        # Deleta os cookies da página
        driver.delete_all_cookies()

        for cookie in cookies:
            # Verifica a chave 'expiry' do cookie (que é um dicionário)
            if isinstance(cookie.get('expiry'), float):
                cookie['expiry'] = int(cookie['expiry']) 

            # Aplica o valor da chave no driver da página
            driver.add_cookie(cookie)
        print("Os cookies foram aplicados com sucesso!")

    except:
        print("Houve um problema ao aplicar os cookies")
        raise Exception
    
    return driver

def write_csv(nome,user,tweet_date,tweet_text,words):
    # Abre um arquivo em modo escrita e leitura
    with open(r"..\bases\tweets_{}.csv".format(words), "a+", encoding='utf-8') as csv_file:
        # Definindo os nomes dos campos para cada coluna
        fieldnames = ['Nome', 'Username', 'Data', 'Texto']

        # Cria um dicionário com as linhas do csv
        writer = DictWriter(csv_file, fieldnames=fieldnames)

        # Grava os dados no arquivo csv
        writer.writerow({'Nome': nome, 'Username': user, 'Data': tweet_date, 'Texto': tweet_text})

def scrape_tweets(driver, start_date, end_date, words, lang, max_time, diretorio, page):
    # Autenticação da página
    driver = abre_html(driver, page)
    driver = aplica_cookies(driver, dir=diretorio)

    # Idiomas para filtrar os tweets
    languages = { 1: 'en', 2: 'pt', 3: 'es', 4: 'fr', 5: 'de', 6: 'ru', 7: 'zh'}

    # Construção da URL para busca avançada
    url = "https://twitter.com/search?q="
    url += "%24{0}%20(%24{0})".format(words)
    if lang != 0:
        url += "%20lang%3A{}".format(languages[lang])
    url += "%20until%3A{0}%20since%3A{1}".format(end_date, start_date)
    url += "%20-filter%3Areplies&src=typed_query"
    driver.get(url)
    
    # Rolar página pelo tempo estabelecido
    start_time = time.time()
    while (time.time() - start_time) < max_time:
        driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
        time.sleep(5)
        # print('Time left: ',  str(round(max_time - (time.time() - start_time))))

        try:
            # Pegando o código html dos tweets
            tweet_divs = driver.page_source
            soup = BeautifulSoup(tweet_divs, "html.parser")
            content = soup.find_all('article')

            for c in content:
                try:
                    # Capturando o texto do tweet
                    tweet_text = c.find('div', {'data-testid': 'tweetText'}).text
                    
                    # Capturando o nome da pessoa que fez o tweet
                    tweet_name = c.find('div', {'data-testid': 'User-Name'}).text.strip()
                    name_parts = tweet_name.split('@')
                    nome = name_parts[0]
                    user = '@' + name_parts[1].split('·')[0]

                    # Capturando a data do tweet
                    date_elem = c.find('time')
                    tweet_date = date_elem.text.strip()

                    print(f"Nome: {nome}")
                    print(f"User: {user}")
                    print(f"Data: {tweet_date}")
                    print(f"Tweet: {tweet_text}")
                    print("----------------------")

                    try:
                        write_csv(nome,user,tweet_date,tweet_text,words)
                    except:
                        print('csv error')

                except:
                    pass

        except Exception as e:
            print("Algo de errado aconteceu!")
            print(e)
            driver.quit()

def main():
    ''' 
        CÓDIGO PRINCIPAL 
    '''

    # Chave que define o navegador
    driver_type = 2

    # Lista de strings a serem buscadas nos tweets
    words = ['$AMZN']

    # Diretório do arquivo .pkl com os cookies de autenticação de login
    diretorio = '..\pkl'

    # Pagina inicial para autenticação
    page = "https://twitter.com/home"

    # Define o range de datas para a pesquisa
    start_date = '2023-05-27'
    end_date = '2023-06-27'

    # Chave que define o idioma dos tweets
    lang = 2

    # Tempo de busca dos tweets em segundos
    max_time = 60
    
    # Inicializa o navegador
    driver = init_driver(driver_type)

    # Chama a função que faz o scraping passando seus argumentos 
    scrape_tweets(driver, start_date, end_date, words, lang, max_time, diretorio, page)
    time.sleep(5)
    print("Um arquivo com os tweets foi gerado!")

    # Fecha o navegador e encerra sua instância
    driver.quit()


if __name__ == "__main__":
    '''
        EXECUÇÃO DO ESCOPO PRINCIPAL
    '''
    main()