#!/bin/bash
get_build_id() {
  if [[ $VERACODE_SANDBOX_ID ]]
  then
    java -jar /tmp/VeracodeJavaAPI.jar -vid $VERACODE_API_ID  -vkey $VERACODE_API_KEY -action getbuildinfo -appid $VERACODE_APP_ID -sandboxid $VERACODE_SANDBOX_ID -format csv > /tmp/build_info.csv
  else
    java -jar /tmp/VeracodeJavaAPI.jar -vid $VERACODE_API_ID  -vkey $VERACODE_API_KEY -action getbuildinfo -appid $VERACODE_APP_ID -format csv > /tmp/build_info.csv
  fi
  build_id=$(head -2 /tmp/build_info.csv | tail -1 | cut -f1 -d,)
 }

get_app_name() {
  java -jar /tmp/VeracodeJavaAPI.jar -vid $VERACODE_API_ID  -vkey $VERACODE_API_KEY -action getappinfo -appid $VERACODE_APP_ID -format csv > /tmp/app_info.csv
  app_name=$(head -2 /tmp/app_info.csv | tail -1 | cut -f2 -d, | tr -d '"')
 }

get_build_id
get_app_name

get_passfail_status() {
  java -jar /tmp/VeracodeJavaAPI.jar -vid $VERACODE_API_ID -vkey $VERACODE_API_KEY -action passfail -buildid $build_id -appname "${app_name}" -format csv > /tmp/status_info.csv
  passfail_status=$(head -2 /tmp/status_info.csv | tail -1 | cut -f5 -d,)
}

while :
do
echo "Checking status of scan: $build_id"
get_passfail_status

RC=1
if [[ $passfail_status == *"Did Not Pass"* ]]
then
  echo "Scan did not pass."
  echo "Scan found security vulnerabilities."
  break
fi

if  [[ $passfail_status == *"Pass"* ]]
then
  echo "Scan passed."
  echo "Scan did not find any vulnerabilities."
  RC=0
  break
else
  echo "Waiting for Veracode scan to complete."
  echo "Requesting status update in 120 seconds."
  sleep 120;
  continue
fi
done

exit $RC
