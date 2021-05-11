analysis:
	mkdir -p figures
	mkdir -p stats
	python3 dbc_rerp_analysis.py

clean:
	rm -rf figures
	rm -rf stats
