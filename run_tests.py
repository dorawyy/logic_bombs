import os
import re
import subprocess
import template_parser as tpp
import script_runner as sr
import shutil


def ATKrun(cmds_tp, tp_path, src_dirs, prefix, func_name='sym_checker', default_stdin_len=10):
    def params_list_parser(params):
        if len(params.strip()) == 0:
            return []
        else:
            params = params.split(',')
            params = list(map(str.strip, params))
            res = []
            var_pattern = re.compile(r'([a-zA-Z_][a-zA-Z0-9_*]*|\*+)')
            for param in params:
                tmp = var_pattern.findall(param)
                if len(tmp) < 2:
                    raise SyntaxError(', '.join(params))
                var_name = tmp[-1]
                var_type = ' '.join(tmp[:-1])
                var_type = re.sub(r'[ \t\n]*\*', '*', var_type)
                res.append((var_type, var_name))
            print(res)
            return res

    CORRECT = 0
    PARTIAL_CORRECT = 1
    RunTERROR = 2
    CompTError = 3
    TLE = 4

    MAX_TIME = 60
    test_results = {}

    func_pattern = re.compile(r'int[ \t\n]+%s\(([^)]*)\);*' % func_name)

    for src_dir in src_dirs:
        print('===========')
        print('In dir ' + src_dir)
        for root, dirs, files in os.walk(src_dir):
            for file in files:
                cmds = []
                fp = os.path.join(root, file)
                print('-----------------------------')
                print(fp)
                with open(fp) as f:
                    content = f.read()
                finds = func_pattern.findall(content)
                if len(finds) > 1:
                    raise SyntaxError(repr(finds) + '. Duplicated definition!')
                elif len(finds) == 0:
                    continue
                else:
                    params = finds[0].strip()
                    params_list = params_list_parser(params)
                    vars_list = [_[1] for _ in params_list]
                    params = ', '.join(vars_list)

                init_vars = dict(vp=params_list, params=params)
                tp = tpp.TemplateParser(tp_path)
                sruner = sr.ScriptRunner(init_vars)
                res = sruner.run(tp.parse()[0])
                res = '\n'.join(res[1])
                res = tp.replace([res, ])
                print(res)
                res = '\n'.join([content, res])
                outname = file if len(file.split('.')) == 1 else file.split('.')[0]

                if prefix == 'angr':
                    cmds.append(cmds_tp[0] % outname)
                    cmds.append(cmds_tp[1] % (default_stdin_len, outname))

                    # Compile
                    p = subprocess.Popen(cmds[0].split(' '), stdin=subprocess.PIPE)
                    p.communicate(res.encode('utf8'))
                    cp_value = p.wait()
                    if cp_value:
                        test_results[fp] = CompTError
                        print('========= Compile Error! ==========')
                        continue
                    # Run test
                    p = subprocess.Popen(cmds[1].split(' '))
                    try:
                        rt_vale = p.wait(timeout=MAX_TIME)
                        test_results[fp] = rt_vale
                    except subprocess.TimeoutExpired:
                        test_results[fp] = TLE
                        p.kill()

                elif prefix == 'klee':
                    if not os.path.exists('klee'):
                        os.mkdir('klee')
                    with open('klee/a.c', 'w') as f:
                        f.write(res)

                    cmds.append(cmds_tp[0] % outname)
                    cmds.append(cmds_tp[1] % outname)
                    cmds.append(cmds_tp[2] % 2)
                    p = subprocess.Popen(cmds[0].split(' '), stdin=subprocess.PIPE)
                    p.communicate(res.encode('utf8'))
                    cp_value = p.wait()
                    if cp_value:
                        test_results[fp] = CompTError
                        print('========= Compile Error! ==========')
                        continue

                    p = subprocess.Popen(cmds[1].split(' '))
                    rt_vale = p.wait()
                    p = subprocess.Popen(cmds[2].split(' '))
                    try:
                        rt_vale = p.wait()
                        test_results[fp] = rt_vale
                    except subprocess.TimeoutExpired:
                        test_results[fp] = TLE
                        p.kill()
                    shutil.rmtree('klee')
    return test_results

if __name__ == '__main__':
    cmds_tp_angr = ["gcc -Iinclude -Lbin -o angr/%s.out -xc - -lutils -lpthread -lcrypto -lm",
               "python script/angr_run.py -r -l%d angr/%s.out"]

    cmds_tp_klee = [
        "clang -Iinclude -Lbin -emit-llvm -o klee/%s.bc -c -g klee/a.c -lpthread -lutils -lcrypto -lm",
        "klee klee/%s.bc",
        "python3 script/klee_run.py -e%d"
    ]

    tp_path = 'templates/angr.c'

    src_dirs = [
        'src/covert_propogation',
        # 'src/exception_handling',
        'src/external_functions',
        'src/floatpoint',
        # 'src/hash',
        'src/overflow',
        'src/parallel_program',
        'src/symbolic_array',
        'src/symbolic_jump',
        'src/symbolic_value',
        # 'symbolic_variable',
    ]

    res = ATKrun(cmds_tp_angr, tp_path, src_dirs, 'angr')
    print(res)
    import json
    with open('res.json', 'w') as f:
        json.dump(res, f)
