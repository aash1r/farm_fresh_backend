import pandas as pd
from typing import List, Dict, Tuple, Optional, Set
import os
from enum import Enum

class MangoType(str, Enum):
    """Types of mangoes available"""
    SINDHRI = "Sindhri"
    LANGHRA = "Langhra"
    CHAUNSA = "Chaunsa"
    RATOL = "Ratol"

class DeliveryService:
    """Service to handle delivery options for mangoes"""
    
    def __init__(self):
        self.base_path = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
        self.airport_data = None
        self.zipcode_data = {}
        self.sheet_to_state_map = {}
        self.state_to_sheet_map = {}
        self.special_pricing_states = ["IAH", "DFW"]
        self._load_data()
    
    def _load_data(self):
        """Load data from Excel files"""
        # Load airport data
        airport_file = os.path.join(self.base_path, "DESTINATION LIST.xlsx")
        self.airport_data = pd.read_excel(airport_file)
        
        # Clean up airport data
        self.airport_data = self.airport_data[['AIRPORT LIST', 'AIRPORT CODE', 'ZIP CODE', 'STATES']]
        self.airport_data.columns = ['airport_name', 'airport_code', 'zip_code','states']
        
        # Load zipcode data from multiple sheets
        zipcode_file = os.path.join(self.base_path, "120MILES RADIUS.xlsx")
        excel = pd.ExcelFile(zipcode_file)
        
        # Use sheet names directly as state identifiers
        # In this case, sheet names like "CHICAGO", "BALTIMORE", "IAD", etc. are the state identifiers
        for sheet_name in excel.sheet_names:
            # Store the sheet name as the state identifier
            self.sheet_to_state_map[sheet_name] = sheet_name
            self.state_to_sheet_map[sheet_name] = sheet_name
            
            # Check if this is a special pricing state (IAH or DFW)
            if "IAH" in sheet_name or "DFW" in sheet_name:
                # These states have special pricing ($59.99 for 2 boxes, $119.99 for 4 boxes)
                if sheet_name not in self.special_pricing_states:
                    self.special_pricing_states.append(sheet_name)
            
            # Load the data from each sheet
            df = pd.read_excel(zipcode_file, sheet_name=sheet_name)
            self.zipcode_data[sheet_name] = df
        
        # Create a list of available states
        self.available_states = list(self.state_to_sheet_map.keys())
        print(self.available_states,'dss')
    
    def get_airports(self) -> List[Dict]:
        """Get list of available airports for pickup"""
        airports = []
        for _, row in self.airport_data.iterrows():
            if pd.notna(row['airport_name']) and pd.notna(row['airport_code']) and pd.notna(row['zip_code']):
                airports.append({
                    'name': row['airport_name'],
                    'code': row['airport_code'],
                    'zip_code': str(int(row['zip_code'])) if pd.notna(row['zip_code']) else None
                })
        return airports
    
    def get_available_states(self) -> List[str]:
        """Get list of available states for doorstep delivery
        
        Returns:
            List[str]: List of available state names (without ZIP codes)
        """
        # Get sheet names from the zipcode data
        sheet_names = list(self.zipcode_data.keys())
        
        # Clean up the state names by removing ZIP codes
        clean_state_names = []
        for sheet_name in sheet_names:
            # Split by space and take only the first part (state name)
            parts = sheet_name.split()
            if parts:
                # For states with multiple words (e.g., 'NEW YORK'), join all parts except the last one (ZIP code)
                if len(parts) > 2:
                    state_name = ' '.join(parts[:-1])  # Join all parts except the last one
                else:
                    state_name = parts[0]  # Just take the first part
                clean_state_names.append(state_name)
        
        return clean_state_names
        
    def get_mango_types(self) -> List[str]:
        """Get list of available mango types"""
        return [mango.value for mango in MangoType]
        
    def get_pickup_allowed_quantities(self) -> List[int]:
        """Get allowed quantities for pickup delivery"""
        return [8, 12, 16, 20, 24]
        
    def get_doorstep_allowed_quantities(self) -> List[int]:
        """Get allowed quantities for doorstep delivery"""
        return [2, 4]
        
    def calculate_pickup_price(self, mango_type: str, quantity: int) -> float:
        """Calculate price for pickup delivery based on mango type and quantity"""
        if mango_type not in [m.value for m in MangoType]:
            raise ValueError(f"Invalid mango type: {mango_type}")
            
        if quantity not in self.get_pickup_allowed_quantities():
            raise ValueError(f"Invalid quantity for pickup: {quantity}")
            
        # Pricing for Ratol mangoes
        if mango_type == MangoType.RATOL.value:
            if quantity == 8:
                return 264.0  # $33/box
            elif quantity == 12:
                return 384.0  # $32/box
            elif quantity == 16:
                return 496.0  # $31/box
            elif quantity == 20:
                return 620.0  # $31/box
            elif quantity == 24:
                return 744.0  # $31/box
        # Pricing for other mango types (Sindhri, Langhra, Chaunsa)
        else:
            if quantity == 8:
                return 256.0  # $32/box
            elif quantity == 12:
                return 372.0  # $31/box
            elif quantity == 16:
                return 480.0  # $30/box
            elif quantity == 20:
                return 600.0  # $30/box
            elif quantity == 24:
                return 720.0  # $30/box
                
        # Should never reach here
        return 0.0
        
    def calculate_doorstep_price(self, state: str, quantity: int) -> float:
        """Calculate price for doorstep delivery based on state and quantity
        
        Args:
            state: The state name (e.g., 'CHICAGO', 'NEW YORK')
            quantity: Number of boxes (2 or 4)
            
        Returns:
            float: The calculated price
        """
        # Find the matching sheet for this state name
        matching_sheet = None
        for sheet_name in self.zipcode_data.keys():
            # Extract state name from sheet name
            parts = sheet_name.split()
            if parts:
                if len(parts) > 2:
                    sheet_state = ' '.join(parts[:-1])
                else:
                    sheet_state = parts[0]
                    
                if sheet_state == state:
                    matching_sheet = sheet_name
                    break
        
        # Check if we found a matching sheet
        if not matching_sheet:
            raise ValueError(f"Invalid state: {state}")
            
        if quantity not in self.get_doorstep_allowed_quantities():
            raise ValueError(f"Invalid quantity for doorstep: {quantity}")
            
        # Special pricing for IAH and DFW states
        if "IAH" in matching_sheet or "DFW" in matching_sheet:
            if quantity == 2:
                return 59.99
            elif quantity == 4:
                return 119.99
        # Regular pricing for other states
        else:
            if quantity == 2:
                return 69.99
            elif quantity == 4:
                return 135.99
                
        # Should never reach here
        return 0.0
        
        """Get list of available states for doorstep delivery"""
        return self.available_states
    
    def validate_zipcode(self, zipcode: str, state: str) -> Tuple[bool, Optional[str]]:
        """Validate if zipcode is available for delivery in the given state
        
        Args:
            zipcode: The zipcode to validate
            state: The state name (e.g., 'CHICAGO', 'NEW YORK')
            
        Returns:
            Tuple[bool, Optional[str]]: (is_valid, error_message)
        """
        # Find the matching sheet for this state name
        matching_sheet = None
        for sheet_name in self.zipcode_data.keys():
            # Extract state name from sheet name
            parts = sheet_name.split()
            if parts:
                if len(parts) > 2:
                    sheet_state = ' '.join(parts[:-1])
                else:
                    sheet_state = parts[0]
                    
                if sheet_state == state:
                    matching_sheet = sheet_name
                    break
        
        # Check if we found a matching sheet
        if not matching_sheet:
            return False, f"State {state} is not available for doorstep delivery"
        
        # Get the data for this state
        df = self.zipcode_data[matching_sheet]
        zipcode_exists = False
        
        # Check all columns in the dataframe for the zipcode
        for col in df.columns:
            for idx, value in df[col].items():
                # Convert to string and handle NaN values
                if pd.notna(value):
                    # Convert numeric values to integers to remove decimal points
                    if isinstance(value, (int, float)):
                        value_str = str(int(value))
                    else:
                        value_str = str(value).strip()
                        
                    if value_str == zipcode:
                        zipcode_exists = True
                        break
            if zipcode_exists:
                break
        
        if not zipcode_exists:
            # Check if zipcode exists in any other state's sheet
            matching_other_state = None
            for other_sheet, other_df in self.zipcode_data.items():
                if other_sheet == matching_sheet:
                    continue
                
                for col in other_df.columns:
                    for idx, value in other_df[col].items():
                        if pd.notna(value):
                            # Convert numeric values to integers to remove decimal points
                            if isinstance(value, (int, float)):
                                value_str = str(int(value))
                            else:
                                value_str = str(value).strip()
                                
                            if value_str == zipcode:
                                # Extract state name from the other sheet
                                other_parts = other_sheet.split()
                                if other_parts:
                                    if len(other_parts) > 2:
                                        other_state = ' '.join(other_parts[:-1])
                                    else:
                                        other_state = other_parts[0]
                                    matching_other_state = other_state
                                break
                    if matching_other_state:
                        break
                if matching_other_state:
                    break
            
            if matching_other_state:
                return False, f"Zipcode {zipcode} belongs to {matching_other_state}, not {state}"
            else:
                return False, f"Zipcode {zipcode} is not available for doorstep delivery"
        
        return True, None
        
    def validate_mango_order(self, delivery_type: str, mango_types: List[str], quantities: List[int]) -> Tuple[bool, Optional[str], float]:
        """Validate mango order based on delivery type and selection rules
        
        Args:
            delivery_type: 'pickup' or 'doorstep'
            mango_types: List of mango types ordered
            quantities: List of quantities for each mango type
            
        Returns:
            Tuple[bool, Optional[str], float]: (is_valid, error_message, total_price)
        """
        if len(mango_types) != len(quantities):
            return False, "Mismatch between mango types and quantities", 0.0
            
        # Filter out zero quantities
        filtered_types = []
        filtered_quantities = []
        for i, qty in enumerate(quantities):
            if qty > 0:
                filtered_types.append(mango_types[i])
                filtered_quantities.append(qty)
                
        mango_types = filtered_types
        quantities = filtered_quantities
        
        # Validate mango types
        valid_types = [m.value for m in MangoType]
        for mango_type in mango_types:
            if mango_type not in valid_types:
                return False, f"Invalid mango type: {mango_type}", 0.0
        
        total_quantity = sum(quantities)
        total_price = 0.0
        
        # Pickup delivery validation
        if delivery_type == "pickup":
            # Rule: Minimum 8 boxes
            if total_quantity < 8:
                return False, "Pickup orders require a minimum of 8 boxes", 0.0
                
            # Rule: No mixing of types
            if len(mango_types) > 1:
                return False, "Pickup orders cannot mix different mango types", 0.0
                
            # Rule: Only allowed quantities
            allowed_quantities = self.get_pickup_allowed_quantities()
            if total_quantity not in allowed_quantities:
                return False, f"Pickup orders must be one of these quantities: {allowed_quantities}", 0.0
                
            # Calculate price
            total_price = self.calculate_pickup_price(mango_types[0], total_quantity)
            
        # Doorstep delivery validation
        elif delivery_type == "doorstep":
            # Rule: Only allowed box counts: 2 or 4
            allowed_quantities = self.get_doorstep_allowed_quantities()
            if total_quantity not in allowed_quantities:
                return False, f"Doorstep orders must be either 2 or 4 boxes in total", 0.0
                
            # Rule: Max 2 mango categories can be mixed
            if len(mango_types) > 2:
                return False, "Doorstep orders can mix at most 2 different mango types", 0.0
                
            # Calculate price based on state (will be updated later with actual state)
            # For now, use regular pricing
            total_price = 69.99 if total_quantity == 2 else 135.0
        else:
            return False, f"Invalid delivery type: {delivery_type}", 0.0
            
        return True, None, total_price

# Create a singleton instance
delivery_service = DeliveryService()
