$PATH=$(PWD)

$UnixLikePath = $PWD_DIR -replace '\\', '/'

docker run --name kpi-engine -v $PATH/app:/kpi-engine -p 8000:8000 kpi-engine