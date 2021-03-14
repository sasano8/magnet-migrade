import typer

app = typer.Typer()


@app.command()
def run(numprocesses: int = 6, cov: bool = False) -> None:
    """テストを実行します。"""
    import subprocess
    import sys

    args = ["python3", "-m", "pytest"]
    if numprocesses > 1:
        args.append(f"-n{numprocesses}")
    args.append("tests")
    args.append("-v")
    if cov:
        args.append("--cov=magnet")
        args.append("--cov=framework")
        args.append("--cov=pp")
        args.append("--cov=pandemic")
        args.append("--cov=rabbitmq")
        args.append("--cov-report=html")
    sys.stdout.write(" ".join(args))

    proc = subprocess.Popen(args, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    rc = 0
    while proc.poll() is None:
        output = proc.stdout.readline()  # type: ignore
        if output:
            sys.stdout.write("\n" + output.strip().decode())
        rc = proc.poll()  # type: ignore
    sys.stdout.write("\n")
    # TODO: テスト失敗時にエラーコードが取得できない
    return rc
