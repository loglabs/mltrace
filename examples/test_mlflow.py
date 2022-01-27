from mltrace import Component
import mlflow
 
 
new_component = Component("test", "boyuan")
 
 
@new_component.run(auto_log=True)
def test_mlflow_run_id():
    mlflow.start_run()
   
    mlflow.log_param("param1", 1)
 
    mlflow.log_metric("foo", 1)
    mlflow.log_metric("foo", 2)
    mlflow.log_metric("zoo", 1)
    print("hello")
    mlflow.end_run()
 
 
test_mlflow_run_id()
