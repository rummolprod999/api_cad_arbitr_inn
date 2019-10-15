import logging

import init_service
import router


def main():
    init_service.initializator()
    logging.info("start")
    logging.info("end")


if __name__ == '__main__':
    main()
    router.app.run(debug=True, host='0.0.0.0')
    # model_by_inn.return_arb('5835115265')
