def expense():
    echo('Expenses ...')


def fetch():
    pass

def add():
    pass

def edit():
    pass

def delete():
    pass


def init_commands(group):
    g = group()(expense)
    g.command()(add)
    g.command()(fetch)
    g.command()(add)
    g.command()(edit)
    g.command()(delete)