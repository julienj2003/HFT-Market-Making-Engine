from decimal import Decimal

class InventoryManager:
    def __init__(self, max_position: float = 10.0):
        self.position = Decimal("0.0")
        self.max_position = Decimal(str(max_position)) # prevent over exposure

    def update_position(self, fill_qty: Decimal):
        new_position = self.position + fill_qty

        if abs(new_position) > self.max_position:
            print(f"WARNING Trade rejected: Position would exceed {self.max_position} BTC")
            return False
        
        self.position = new_position
        return True
    
    def simulate_fill(self, side: str, qty: float = 0.1):
        fill_qty = Decimal(str(qty))
        if side.lower() == "sell":
            fill_qty = -fill_qty
            
        success = self.update_position(fill_qty)
        if success:
            print(f"[FILL] Simulated {side.upper()} of {qty} BTC // New Position: {self.position}")
        return success
    
    def get_position(self) -> Decimal:
        """Returns the current BTC position for the Quoter."""
        return self.position
