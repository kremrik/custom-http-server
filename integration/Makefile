CONTAINER := socket-testing

build:
	docker build -t $(CONTAINER) .

serve:
	echo 'Forwarding port 8080...'
	docker run --rm \
		--name $(CONTAINER) \
		-p 8089:443 \
		--add-host host.docker.internal:host-gateway \
		$(CONTAINER)

logs:
	docker logs -f $(CONTAINER)

shell-into:
	docker exec -it $(CONTAINER) bash

stop:
	docker stop $(CONTAINER)
