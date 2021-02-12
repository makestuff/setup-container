# Build the image
docker image rm -f makestuff:0.1; docker builder prune -f
docker build --tag makestuff:0.1 .

# Run the image, with an example Codespaces-ready repo
docker run -p 127.0.0.1:8080:8080/tcp --name ${USER}-1 --user vscode -it makestuff:0.1 /usr/local/bin/setup-container.py https://github.com/makestuff/vscode-foo.git

# Reconnect
docker start -ai ${USER}-1

# Check available containers
docker ps --all

# Connect
http://localhost:8080

# Destroy container
docker rm --force ${USER}-1
