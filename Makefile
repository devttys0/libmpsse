
python-wheel:
	docker run -it -v $(PWD):/io quay.io/pypa/manylinux1_x86_64 /io/build_wheels.sh

clean:
	sudo rm -rf wheelhouse
