all: clean unit deploy setup integration

unit:
	cd "../src/tests/unit/" && pytest --log-cli-level=ERROR
	
deploy:
	./deploy.sh

setup: 
	python3 ./insert_permission_documents.py

integration:
	cd "../src/tests/integration/" && pytest --log-cli-level=INFO

clean:
	python3 ./clear_dynamodb_table.py
