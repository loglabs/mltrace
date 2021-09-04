# DVC integration with MLFlow example
DVC (Data Version Control) allows us to version data pipelines ie. the series of processing stages that we apply to our raw dataset to produce a final result.

By versioning pipelines, we can backtrack to a previous version of a model or dataset, re-run a pipeline to reproduce a colleague's work, or update our results given fresh code or data. 

This versioning capability is particularly useful when we combine it with the tracing features of `mltrace`. For example, given the entire lineage of a `Component` or `ComponentRun` that we want to investigate, we can revert to a previous version of the code, data or any intermediate artifacts. After backtracking, we can then troubleshoot by comparing outputs between pipeline versions. 

We might also simplify how we stitch together multiple `mltrace` `Component`s. Specify each data processing stage, its dependencies, inputs and outputs inside a `dvc run` command, and subsequently a `dvc repro` call will automatically re-run the pipeline, refreshing and versioning any newly updated code, data or model / report artifact along the way. 

Integrating DVC and `mltrace` is possible by applying git tags to each code commit. Then, given a `Component` or `ComponentRun` dependency we are interested in, we can run `dvc get [dvc-repo-url/path] [output-path] --rev [git-tag]` to "checkout" the version of the artefact we want. 

Below is a complete example of how DVC might be used with `mltrace`:

**Note that this example assumes that you have already [installed](https://dvc.org/doc/install) DVC and [initialised](https://dvc.org/doc/start) DVC inside your current git repo** 

# Folder Setup 
For this example, we use data collected on [abalone ecology](https://archive.ics.uci.edu/ml/datasets/abalone) available from the UCI Machine Learning Repository. With this dataset, the goal is to predict the age of the abalone (measured through its number of rings) using features such as it's whole weight, diameter and height. 

Download the data and place it into a folder named `data/` at the root of this `dvc-mltrace` folder. 

.  
├── 01_clean_data.py  # file for first stage of pipeline where data is cleaned  
├── 02_summary_stats.py  # code for second stage of pipeline with summary stats  
├── README.md  
├── data  
│    ├── abalone.csv  # file output from first stage of pipeline  
│    ├── abalone.data  # raw data   
│    └── abalone.data.dvc  # file with hash of raw data that dvc uses to track dataset versions  
├── dvc.lock  # file that tracks file hashes associated with each pipeline stage
├── dvc.yaml  # file containing metadata associated with each stage in a pipeline  
└── dvc_run.sh  # bash script containing dvc run commands

# Steps
1. We start with a first cut of a data cleaning component that we call `clean`
```
@register(component_name="clean", input_vars=['input_filepath'], output_vars=['output_filepath'])
def clean(input_filepath: str, output_filepath: str) -> str:
    """
    process raw data by adding column names
    """
    raw = pd.read_csv(input_filepath, header=None)
    print('adding column names')
    raw.columns = ['sex','length','diameter','height','whole_weight','shucked_weight','viscera_weight','shell_weight','rings']
    print('saving data to csv')
    raw.to_csv(output_filepath, index=False)
```  
2. Check that the pipeline works by running `dvc repro`. Additionally, you can view the `dvc.yaml` file for an overview of each stage within our pipeline, and the dependencies associated with each stage. Trace the pipeline with `mltrace recent` or accessing the `mltrace` UI.  
3. Version this pipeline simply by commiting the `dvc.lock` file and adding a git tag to the commit.
```
git add dvc.lock 
git commit -m "dvc.lock file containing first version of pipeline"
git tag -a orig-features -m "dataset with only original features included"  
```
3. Update the `clean` component with additional code to split the continuous column `rings` into discrete quantiles:
```@register(component_name="clean", input_vars=['input_filepath'], output_vars=['output_filepath'])
def clean(input_filepath: str, output_filepath: str) -> str:
    """
    process raw data by adding column names
    """
    raw = pd.read_csv(input_filepath, header=None)
    print('adding column names')
    raw.columns = ['sex','length','diameter','height','whole_weight','shucked_weight','viscera_weight','shell_weight','rings']
    print('adding rings quantiles column')
    quantile_labels = ['young', 'middle_aged', 'old']  # new code 
    raw['rings_quantile'] = pd.qcut(raw['rings'], q=3, precision=0, labels=quantile_labels)  # new code
    print('saving data to csv')
    raw.to_csv(output_filepath, index=False)
```
4. Update the versions of the pipeline's dependencies 
```
dvc repro
git add dvc.lock
git commit -m "updated dvc.lock with new clean stage" 
```
Note that we can see that the file hash of `clean`'s output inside the `dvc.lock` file has been updated. 
```
- path: data/abalone.csv
      md5: 9b51a9e8ad4d80f58f6bc9cfc54b1202
```
5. Add requisite git tag to this pipeline version
```
git tag -a "rings_quantile" -m "added quantiles of rings as a feature"
```
6. Now, if we no longer want the additional `rings_quantile` column, and want to revert back to an earlier version of our code and dependencies, we can use the `orig-features` git tag we specified previously. 
```
git checkout orig-features
```
we can see that the file hash in the `dvc.lock` file has reverted to our earlier version
```
outs:
    - path: data/abalone.csv
      md5: 68821df28b91c28a287a67a6cb2a1bda
```
7. Confirm this revision by running `dvc checkout` which will restore the original state of the code and data
```
dvc checkout
```
8. Alternatively, we can be selective about what we revert by running either 
```
dvc checkout data/abalone.csv  # dvc checkout [file]
```
or 
```
dvc get . data/abalone.csv --rev orig-features  # dvc get [dvc-repo-url/path] [output-path] --rev [git-tag]
```
More information on navigating between repo versions can be found [here](https://dvc.org/doc/command-reference/checkout#example-automating-dvc-checkout)
