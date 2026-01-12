import grpc
from hr.grpc.employee import employee_pb2_grpc
from hr.grpc.employee import employee_pb2



def run():
    with grpc.insecure_channel("localhost:50053") as channel:
        stub = employee_pb2_grpc.EmployeeServiceStub(channel)

        try:
            response = stub.ValidateEmployee(
                employee_pb2.ValidateEmployeeRequest(
                    employee_id="EMP-1001w"
                )
            )
        except Exception as e:
            print(e.details)
            return

        print("Employee ID:", response.employee_id)
        print("Employee Name:", response.employee_name)


if __name__ == "__main__":
    run()
