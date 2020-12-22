import os
os.environ['LD_LIBRARY_PATH'] = '/home/klee/klee_build/lib/:$LD_LIBRARY_PATH'
lib_path = '/home/klee/klee_build/lib/'

# ============ run_tests Setting ==============
FUNC_NAME = 'logic_bomb'


cmds_tp_angr = ["clang -Iinclude -Lbuild -o angr/%s.out -xc - -lutils -lpthread -lcrypto -lm",
            "python script/angr_run.py -r -l%d angr/%s.out"]

cmds_tp_angr_cpp = ["clang++ -Iinclude -Lbuild -o angr/%s.out -xc++ - -lutils -lpthread -lcrypto -lm",
            "python script/angr_run.py -r -l%d angr/%s.out"]

cmds_tp_klee = [
    #"clang -Iinclude -Lbuild -Wno-unused-parameter -emit-llvm -o klee/%s.bc -c -g klee/a.c -lpthread -lutils -lcrypto -lm",
    "clang -Iinclude -I/home/klee/klee_src/include -L/home/klee/klee_build/lib/ -Llib -Wno-unused-parameter -emit-llvm -o klee/%s.bc -c -g klee/a.c -lpthread -lutils -lcrypto -lm",
    "klee --libc=uclibc --posix-runtime klee/%s.bc",
    "python3 script/klee_run.py -e%d -p%s"
]

cmds_tp_triton = [
    "clang -Iinclude -Lbuild -o triton/%s.out -xc - -lutils -lpthread -lcrypto -lm",
    "python script/triton_caller.py -l%d -m%d -f%s -i%s -p triton/%s.out"
]

cmds_tp_triton_cpp = [
    "clang++ -Iinclude -Lbuild -o triton/%s.out -xc++ - -lutils -lpthread -lcrypto -lm",
    "python script/triton_caller.py -l%d -m%d -f%s -i%s -p triton/%s.out"
]


cmds_tp_crest = [
    "mkdir crest/out_%s && cd crest/out_%s && cp ../a.c %s.c && sudo crestc ../a.c &> out_crestc_%s.txt",
    "sudo run_crest a 100 -cfg &> out_runcrest_%s.txt && cd ../",
    "python3 script/crest_run.py -e%d -p%s"
]

angr_tp_path = 'templates/default_no_printf.c'
triton_tp_path = 'templates/default_no_printf.c'
klee_tp_path = 'templates/klee.c'
crest_tp_path = 'templates/crest.c'

switches = {
    'angr': [cmds_tp_angr, angr_tp_path, 'angr', ('src/', )],
    'angr_cpp': [cmds_tp_angr_cpp, angr_tp_path, 'angr', ('src_cpp/', )],
    'triton': [cmds_tp_triton, triton_tp_path, 'triton', ('src/', )],
    'triton_cpp': [cmds_tp_triton_cpp, triton_tp_path, 'triton', ('src_cpp/', )],
    'klee': [cmds_tp_klee, klee_tp_path, 'klee', ('src/', )],
    'crest': [cmds_tp_crest, crest_tp_path, 'crest', ('src/', )],
}

# ============ triton Setting ==============
TRITON_INSTALLATION_PATH = '/home/neil/Triton/build/triton' # For example, /home/zzrcxb/Triton/build/triton
