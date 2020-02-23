cp $1 ./compile/.
cd compile/

rm * -f

cython $1 --embed -o build.c -3

gcc -o build build.c `pkg-config --cflags --libs python3`

rm *.py *.c

echo "Executing output"
./build

cd ..
