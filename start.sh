if ! [[ -f .complate ]]; then
    echo "Checking depends.."
    (apk update && apk add python3 py3-pip && pip install -r requirements.txt --break-system-packages) &> /dev/nullelse
fi

python app.py