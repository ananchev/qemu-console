#!/bin/bash

function shutdown()
{
  echo `date` " " `whoami` " Received a signal to shutdown"

  # INSERT HERE THE COMMAND YOU WANT EXECUTE AT SHUTDOWN
  /usr/bin/curl "<qemu-console url:port>/host_shutdown"
  # END INSERT
  exit 0
}

function startup()
{
  echo `date` " " `whoami` " Starting..."

  # INSERT HERE THE COMMAND YOU WANT EXECUTE AT STARTUP
  sleep 15
  /usr/bin/curl "<qemu-console url:port>/host_startup"
  # END INSERT
  tail -f /dev/null &
  wait $!
}

trap shutdown SIGTERM
trap shutdown SIGKILL

startup;

