# convert iri file to pixel file

## clone repo etc

```bash
git clone https://github.com/matthiaszimmermann/tmp-iri2pixel.git
cd tmp-iri2pixel
```

## build docker image

```bash
docker build -t iri2pix .
```

## run docker container

run container in interactive 
mode

```bash
docker run -it --rm -v $PWD:/usr/src/app iri2pix bash
```

the above command opens a bash shell inside the container to execute commands.
the command line should now look similar as shown below

```bash
root@a1d2c341a2:/usr/src/app#
```

to quit from the contianer command line use command `exit`

## run conversion inside container

inside container
* show usage of script `iri_to_pixel_csv.py`
* run conversion with script

show usage

```bash
python3 iri_to_pixel_csv.py
usage: iri_to_pixel_csv.py file x y year-from dir-out
```

* `file`: the iri input file
*  `x`: latitude for input file
*  `x`: longitude for intput file
*  `year-from`: the first year to include in the output pixel file
*  `dir-out`: the output directory or the output pixel file (use `.` for the current directory)

run conversion from iri file to pixel file

```bash
python3 iri_to_pixel_csv.py iri_sample_x343_y002.csv 34.3 0.2 1983 .
```

this should produce output file `Pixel744203.csv`.
to verify the output use the checksum tool to compare this output file with the expected output `Pixel744203.reference.csv`.

```bash
cksum Pixel744203.csv Pixel744203.reference.csv
2958646202 76439 Pixel744203.csv
2958646202 76439 Pixel744203.reference.csv
```
