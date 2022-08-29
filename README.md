# Factorio Data.raw to Json

导出异星工厂游戏的数据到json(基于lupa)。

Factorio Data.raw to JSON By Python (with lupa).

## 注意

运行程序的方式是： `get_json.bat 版本` ， 例如：

```bash
get_json.bat 1.1.61
```

它会从 `github.com/wube/factorio-data` 下载数据，并转json。

数据将存储于 “version_data” 文件夹。

JSON文件将存储于 “json_data” 文件夹。

- 文件夹 `v_{version}_data`: data.raw的各个子项json
- 文件 `v_{version}_data.json`: data.raw 转换的json
- 文件 `v_{version}_data_part.json`: data.raw 转换的json但不包含key： noise-expression 和 optimized-particle （这极大的减小了json体积）

注意，为了尽快的让代码跑起来，我用了很多愚蠢的技巧。如：
- 复制游戏数据下的`base`文件夹到`__base__`
- 构造部分存储库不存在但被引用数据、函数
- luatable 转 json 的部分只针对data.raw 的已知 bad case 做了支持，转出来的可能有点奇怪。

更多细节请看代码，几乎支持所有版本（0.16以上）。


## Run the Code

before run the code, please read all readme.md

usage: get_json.bat version

```bash
get_json.bat 1.1.53
```

version >= 0.16.0

(for linux, please check the 'get_json.bat' file, it is easy trans to linux.)

## Process

in get_json.bat:

1. download data from `github.com/wube/factorio-data` to version_data folder
2. run python code: `main.py`

In main.py, the process is:

### 1. fake to lua 

I am a very noob for lua. So, I use some "smart" trick to run the lua code.

a) copy game data `base` folder to `__base__` folder

because some codes try to require `__base__/XXX`

b) fake `menu-simulations.lua` file

project `factorio-data` not include `menu-simulations.lua`

I made a fake empty lua file for it.

In `main.py > get_data_raw()`, also add

- some concatenate strings for lua path
- a function math.pow
- a luatable defines

### 2. luatable to dict

a simple func in tool.py.

notice, its behavior is not standard.

e.g. it have a special op to key `ingredients`.

### 3. convert to json and write file

json file in `./json_data` folder

- folder `v_{version}_data`: every sub-item in data.raw
- file `v_{version}_data.json`: data.raw
- file `v_{version}_data_part.json`: data.raw with out noise-expression and optimized-particle