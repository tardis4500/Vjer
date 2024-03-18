#!/bin/bash
get_results_ready_status() {
  if [[ $VERACODE_SANDBOX_ID ]]
  then
    java -jar /tmp/VeracodeJavaAPI.jar -vid $VERACODE_API_ID  -vkey $VERACODE_API_KEY -action getbuildinfo -appid $VERACODE_APP_ID -sandboxid $VERACODE_SANDBOX_ID -format csv > /tmp/build_info.csv
  else
    java -jar /tmp/VeracodeJavaAPI.jar -vid $VERACODE_API_ID  -vkey $VERACODE_API_KEY -action getbuildinfo -appid $VERACODE_APP_ID -format csv > /tmp/build_info.csv
  fi

  if [[ $RESULTS_READY_INDEX ]]
  then
    INDEX=$RESULTS_READY_INDEX
  else
    INDEX=1
  fi

  while :
  do

  COLUMN_NAME=$(head -1 /tmp/build_info.csv | tail -1 | cut -"f${INDEX}" -d,)

  if [[ $COLUMN_NAME == "RESULTS_READY" ]]
  then
    RESULTS_READY=$(head -2 /tmp/build_info.csv | tail -1 | cut -"f${INDEX}" -d,)
    RESULTS_READY_INDEX=$INDEX
    break
  else
    ((INDEX=INDEX+1))
    continue
  fi

  done
 }


while :
do
get_results_ready_status
echo "Checking status of previous scan."

if [[ $RESULTS_READY == "true" ]]
then
  echo "Next scan is ready to start."
  break
else
  echo "Waiting for current scan to finish."
  echo "Requesting status update in 120 seconds."
  sleep 120;
  continue
fi
done