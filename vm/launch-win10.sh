#!/bin/bash
qemu-system-x86_64 \
    -name "Windows-10" \
    -machine type=pc,accel=kvm \
    -cpu host \
    -smp cores=8,threads=1,sockets=1 \
    -m 16G \
    -device VGA \
    -drive file="$PROJECT_ROOT/build/tmp/Win10_22H2_English_x64v1.iso",media=cdrom,if=ide,index=0 \
    -drive file="$PROJECT_ROOT/vm/bf6-w11-gaming.qcow2",if=ide,index=1,format=qcow2,cache=writeback \
    -netdev user,id=net0 -device e1000,netdev=net0 \
    -enable-kvm \
    -display gtk \
    -boot order=d,menu=off
