from stockwiz import StockWiz


if __name__ == '__main__':
    app = StockWiz()

    need_to_be_download = app.read_list_and_find_not_existed()
    need_to_be_downloaded = sorted(need_to_be_download)
    print(need_to_be_download)

    finished_list, err_list = app.download_stock_data_and_save_json(need_to_be_download)

    app.read_json_file_to_csv()
    app.driver.quit()

    print("Download Fail : >>")
    print(err_list)
