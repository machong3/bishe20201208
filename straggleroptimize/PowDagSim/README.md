##### NOTE
Currently there is a bug with the POWOPT algorithm, consider using the NAIVE algorithm for now.

### Prerequisites:
* `networkx` package
  * To install run `pip install networkx` (or using your favorite Python package manager)
* `toposort` package
  * To install run `pip install toposort`
* `matplotlib`
  * `pip install matplotlib`

## Running the simulation

To run simulation with default parameters: `python main.py`

To see what parameters are available run: `python main.py -h`

The output of the simulation will be a text file stored in the `output` directory.

If not all tasks are completed at the end of the simulation, consider increasing the power cap. For lower power caps, the naive algorithm may not be able to schedule all tasks.

#### Selecting DAGs
Pick any `.dot` file from the `dag` directory, and specify the name using the `-d` parameter. E.g. `python main.py -d swift1`

#### Plotting

After running `main` you can run `python plot.py`. Inside  `plot.py` you can specify which file to plot. Make sure to specify the power cap as the same used during the simulation. *This will hopefully change in the future.*
