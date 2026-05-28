# training-data-pipeline
Minimal ROCm PyTorch environment for ROCm/GPU - AMD Radeon Vega 8 Graphics

   <br/>

## Experimental financial market data pipeline
- **This is a work in progress** Python souce code
- Docker environment for python: pytorch with AMD RocM GPU support   
- Vibe coded with help from [Google Gemini](https://gemini.google.com/app)  
- Parser for market data to prepare training data as jsonl format for training
- Also writes a modified psudeo-jsonl.md file for human readable dataset for analysis
- Note: current sample data is not yet a real trading strategy, need to add more features, etc. 
- Next step is to train a DQNN with the training data for market/trading decision making
- Not Financial Advice! This is Experimental Software. <i><b>Use At Your Own Risk!</b></i>
  
    
    

-----

   <br/>


### Usage
```
# build the container environment
    $ podman build -t localhost/rocm-pytorch .  
# create an output 'data' directory  
    $ mkdir data
# run the container...
    $ ./run-torch-rocm.sh 
# inside the container...
    [workspace]# cd /app
    # prepare training data...
    [app]# python fetch_and_prepare.py
    # view the training data with range discriminator (first 5 records)...
    [app]# python view_training_data.py data/trading_examples.jsonl 5  
# note: the output files will be created on the first run in the data directory  
    [app]# ls -1 data  
         nq_data_yf.db
         trading_examples.jsonl
         trading_examples.jsonl.md
```

### Development System
Operating System: Fedora Linux 43 <br/>
KDE Plasma Version: 6.6.4 <br/>
KDE Frameworks Version: 6.25.0 <br/>
Qt Version: 6.10.3 <br/>
Kernel Version: 6.19.12-200.fc43.x86_64 (64-bit) <br/>
Graphics Platform: Wayland <br/>
Processors: 8 × AMD Ryzen 5 PRO 2500U w/ Radeon Vega Mobile Gfx <br/>
Memory: 8 GiB of RAM (6.6 GiB usable) <br/>
Graphics Processor: AMD Radeon Vega 8 Graphics <br/>
Manufacturer: LENOVO <br/>
Product Name: 20MVS03800 <br/>
System Version: ThinkPad A485 <br/>
  
### Source Files
```
training-data-pipeline/
    ├── Dockerfile
    ├── requirements.txt
    ├── run-torch-rocm.sh
    ├── fetch_and_prepare.py
    ├── view_training_data.py
    ├── LICENSE
    ├── README.md
    ├── data
        ├── nq_data_yf.db
        ├── trading_examples.jsonl
        └── trading_examples.jsonl.md
```

   <br/>


 ## Dataset Viewer

There is an .md format psuedo-jsonl file for human readable analysis of the training data<br/> called data/trading_examples.jsonl.md. Alternatively for a more user friendly analyis of the <br/>training data, use the dataset viewer script to quickly review 
training examples in <br/>a clean, human-readable format. The viewer accepts ranges in a pythonic style format <br/> 
like 1:3 for the first three records, etc.<br/>

### Usage
```bash
python view_training_data.py <path_to_jsonl> [range]
```

### Examples

* **View everything from start to finish:**
  ```bash
  python view_training_data.py data/trading_examples.jsonl
  ```

* **View a single specific record (e.g., Record 5):**
  ```bash
  python view_training_data.py data/trading_examples.jsonl 5:5
  ```

* **View a specific range of records (e.g., Records 3 to 4):**
  ```bash
  python view_training_data.py data/trading_examples.jsonl 3:4
  ```

* **View everything from a specific start point onward (e.g., Record 100 onwards):**
  ```bash
  python view_training_data.py data/trading_examples.jsonl 100:
  ```

* **View everything up to a specific limit (e.g., first 10 records):**
  ```bash
  python view_training_data.py data/trading_examples.jsonl :10
  ```

   <br/>

## Sample Human readable data (view_training_data.py output)

```
[app]# python view_training_data_range2.py trading_examples.jsonl :2  
```

[ 1 ]
  { "role": "user", "content": "
### Recent NQ 1-minute bars:

| time   |     open |     high |      low |    close |   volume |   rsi |   macd |
|:-------|---------:|---------:|---------:|---------:|---------:|------:|-------:|
| 04:09  | 23986.75 | 23990.00 | 23986.00 | 23988.75 |      112 | 69.98 |   0.26 |
| 04:10  | 23989.75 | 23990.00 | 23986.25 | 23988.00 |      129 | 68.70 |   0.57 |
| 04:11  | 23987.00 | 23990.75 | 23986.75 | 23989.25 |      143 | 69.70 |   0.92 |
| 04:12  | 23988.50 | 23989.00 | 23982.25 | 23983.50 |      128 | 60.18 |   0.72 |
| 04:13  | 23983.00 | 23983.75 | 23980.00 | 23982.25 |      141 | 58.32 |   0.45 |
| 04:14  | 23982.00 | 23984.00 | 23980.25 | 23982.50 |      171 | 58.59 |   0.26 |
| 04:15  | 23983.00 | 23984.25 | 23981.00 | 23982.25 |      106 | 58.18 |   0.09 |
| 04:16  | 23982.25 | 23983.00 | 23979.00 | 23979.75 |      197 | 54.05 |  -0.25 |
| 04:17  | 23979.00 | 23986.75 | 23978.25 | 23986.25 |      345 | 61.66 |   0.01 |
| 04:18  | 23985.75 | 23992.25 | 23985.00 | 23989.50 |      365 | 64.80 |   0.47 |
| 04:19  | 23989.25 | 23990.50 | 23986.00 | 23987.75 |      145 | 61.87 |   0.68 |
| 04:20  | 23988.50 | 23989.50 | 23986.00 | 23989.50 |       63 | 63.64 |   0.99 |
| 04:21  | 23989.75 | 23990.25 | 23986.00 | 23989.00 |       87 | 62.74 |   1.17 |
| 04:22  | 23989.25 | 24013.50 | 23989.00 | 24000.75 |     1114 | 72.55 |   2.24 |
| 04:23  | 24000.50 | 24007.00 | 23998.00 | 24004.25 |      649 | 74.69 |   3.33 |
| 04:24  | 24004.25 | 24008.25 | 24000.25 | 24004.00 |      326 | 74.24 |   4.13 |
| 04:25  | 24004.25 | 24005.50 | 24000.75 | 24002.00 |      306 | 70.62 |   4.54 |
| 04:26  | 24000.75 | 24001.25 | 23995.25 | 23997.75 |      307 | 63.53 |   4.48 |
| 04:27  | 23997.25 | 24004.00 | 23997.25 | 24004.00 |      197 | 68.53 |   4.88 |
| 04:28  | 24003.25 | 24004.50 | 23999.00 | 24004.50 |      242 | 68.90 |   5.18 |

Analyze momentum, RSI, and MACD. Recommend next action: Long, Short, or Hold.
Include confidence (0-100), stop-loss ticks from entry, and target ticks.
Reason step-by-step.

  }, {

"role": "assistant", "content": "
> Action: Long  
> Confidence: 75  
> Stop-loss: 10 ticks  
> Target: 20 ticks  
> Reason: MACD histogram is expanding upward. Price support held at 23999.0. The current RSI of 68.9 and MACD of 5.18 support a Long bias for the next 5 minutes.  

  } ]

================================================================================

[ 2 ]
  { "role": "user", "content": "
### Recent NQ 1-minute bars:

| time   |     open |     high |      low |    close |   volume |   rsi |   macd |
|:-------|---------:|---------:|---------:|---------:|---------:|------:|-------:|
| 04:10  | 23989.75 | 23990.00 | 23986.25 | 23988.00 |      129 | 68.70 |   0.57 |
| 04:11  | 23987.00 | 23990.75 | 23986.75 | 23989.25 |      143 | 69.70 |   0.92 |
| 04:12  | 23988.50 | 23989.00 | 23982.25 | 23983.50 |      128 | 60.18 |   0.72 |
| 04:13  | 23983.00 | 23983.75 | 23980.00 | 23982.25 |      141 | 58.32 |   0.45 |
| 04:14  | 23982.00 | 23984.00 | 23980.25 | 23982.50 |      171 | 58.59 |   0.26 |
| 04:15  | 23983.00 | 23984.25 | 23981.00 | 23982.25 |      106 | 58.18 |   0.09 |
| 04:16  | 23982.25 | 23983.00 | 23979.00 | 23979.75 |      197 | 54.05 |  -0.25 |
| 04:17  | 23979.00 | 23986.75 | 23978.25 | 23986.25 |      345 | 61.66 |   0.01 |
| 04:18  | 23985.75 | 23992.25 | 23985.00 | 23989.50 |      365 | 64.80 |   0.47 |
| 04:19  | 23989.25 | 23990.50 | 23986.00 | 23987.75 |      145 | 61.87 |   0.68 |
| 04:20  | 23988.50 | 23989.50 | 23986.00 | 23989.50 |       63 | 63.64 |   0.99 |
| 04:21  | 23989.75 | 23990.25 | 23986.00 | 23989.00 |       87 | 62.74 |   1.17 |
| 04:22  | 23989.25 | 24013.50 | 23989.00 | 24000.75 |     1114 | 72.55 |   2.24 |
| 04:23  | 24000.50 | 24007.00 | 23998.00 | 24004.25 |      649 | 74.69 |   3.33 |
| 04:24  | 24004.25 | 24008.25 | 24000.25 | 24004.00 |      326 | 74.24 |   4.13 |
| 04:25  | 24004.25 | 24005.50 | 24000.75 | 24002.00 |      306 | 70.62 |   4.54 |
| 04:26  | 24000.75 | 24001.25 | 23995.25 | 23997.75 |      307 | 63.53 |   4.48 |
| 04:27  | 23997.25 | 24004.00 | 23997.25 | 24004.00 |      197 | 68.53 |   4.88 |
| 04:28  | 24003.25 | 24004.50 | 23999.00 | 24004.50 |      242 | 68.90 |   5.18 |
| 04:29  | 24004.00 | 24007.75 | 24002.75 | 24007.50 |      258 | 71.08 |   5.59 |

Analyze momentum, RSI, and MACD. Recommend next action: Long, Short, or Hold.
Include confidence (0-100), stop-loss ticks from entry, and target ticks.
Reason step-by-step.

  }, {

"role": "assistant", "content": "
> Action: Hold  
> Confidence: 75  
> Stop-loss: 10 ticks  
> Target: 20 ticks  
> Reason: Indicators are neutral and RSI is midrange. The current RSI of 71.1 and MACD of 5.59 support a Hold bias for the next 5 minutes.  

  } ]


   <br/>

        
---
Author: daveray@daveray.net <br/>
Date: 2026-05-05 <br/>
License: [ Apache 2.0 ](https://www.apache.org/licenses/LICENSE-2.0) <br/>
- Not Financial Advice! This is Experimental Software. <i><b>Use At Your Own Risk!</b></i>

--- 
```
   Copyright 2026 David Ray Reizes <daveray@daveray.net>

   Licensed under the Apache License, Version 2.0 (the "License");
   you may not use this file except in compliance with the License.
   You may obtain a copy of the License at

     http://www.apache.org/licenses/LICENSE-2.0

   Unless required by applicable law or agreed to in writing, software
   distributed under the License is distributed on an "AS IS" BASIS,
   WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
   See the License for the specific language governing permissions and
   limitations under the License.
```
--- 
--- 


