** RabbitMQ
RabbitMQ management Plugin enabled by default at http://localhost:15672
To start rabbitmq:
  brew services start rabbitmq
To restart rabbitmq:
  brew services restart rabbitmq
Or, if you don't want/need a background service you can just run:
  CONF_ENV_FILE="/opt/homebrew/etc/rabbitmq/rabbitmq-env.conf" /opt/homebrew/opt/rabbitmq/sbin/rabbitmq-server

** List running qemu instances with nicely formatted output
credit Sean Swehla: https://gist.github.com/kitschysynq/867caebec581cee4c44c764b4dd2bde7
ps -ef | awk -e '/qemu/ && !/awk/' | sed -e 's/[^/]*//' -e 's/ -/\n\t-/g'


