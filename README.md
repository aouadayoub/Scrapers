# Jobbank Scraper

A web scraping project to collect job data from various sources. The project uses Scrapy for scraping and MongoDB for data storage.

## Installation

1. **Clone the repository:**

    ```bash
    git clone https://github.com/aouadayoub/Scrapers.git
    cd Scrapers/jobbank
    ```

2. **Set up a virtual environment:**

    ```bash
    python -m venv venv
    # On Mac use:
        source venv/bin/activate  
    # On Windows use: 
        venv\Scripts\activate
    ```

3. **Install dependencies:**

    ```bash
    pip install -r requirements.txt
    ```

4. **Ensure MongoDB is installed:**

    Make sure MongoDB is installed on your system. You can download it from [MongoDB's official website](https://www.mongodb.com/try/download/community).

## Usage

1. **Ensure your environment is activated:**

    ```bash
    # On Mac use:
        source venv/bin/activate  
    # On Windows use: 
        venv\Scripts\activate
    ```

2. **Run the scraper:**

    The `go-spider.py` script now automatically starts MongoDB before running the scraper. Execute the following command:

    ```bash
    python jobbank/go-spider.py
    ```

3. **Check logs for output:**

    Logs are stored in `jobbank.log` and provide detailed information about the scraping process.

## Configuration

The Scrapy settings can be configured in the `settings.py` file located in the `jobbank` directory. You can modify the settings to adjust the scraping behavior, such as user agents, download delays, and more.

## Dependencies

The project dependencies are listed in `requirements.txt` and include:

- `scrapy`: For web scraping
- `pymongo`: For MongoDB integration

## Contributing

1. **Fork the repository.**
2. **Create a new branch (`git checkout -b feature-branch`).**
3. **Make your changes.**
4. **Commit your changes (`git commit -am 'Add new feature'`).**
5. **Push to the branch (`git push origin feature-branch`).**
6. **Create a new Pull Request.**

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## Contact

For questions or issues, please contact [ayoubsays@protonmail.com](mailto:ayoubsays@protonmail.com).
