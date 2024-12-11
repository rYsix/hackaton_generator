class Account():
    id = None
    username = None
    orders = []
    new_order = {}

    is_auth = False

    def login(self, id, name, orders):
        self.id = id
        self.username = name
        self.orders = orders
        self.is_auth = True

    def logout(self):
        self.id = None
        self.username = None
        self.orders = []
        self.new_order = {}
        self.is_auth = False