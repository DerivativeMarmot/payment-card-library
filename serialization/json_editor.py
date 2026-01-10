# json_editor.py
import tkinter
import customtkinter
import json
import uuid

class DataManager:
    def __init__(self):
        self.issuers = self.load_json('issuers.json')
        self.cards = self.load_json('cards.json')
        self.card_faces = self.load_json('card_faces.json')
        self.benefits = self.load_json('benefits.json')
        self.card_benefits = self.load_json('card_benefits.json')

    def load_json(self, filename):
        with open(filename, 'r', encoding='utf-8') as f: # Specify encoding
            return json.load(f)

    def save_data(self):
        with open('cards.json', 'w', encoding='utf-8') as f:
            json.dump(self.cards, f, indent=2)
        with open('benefits.json', 'w', encoding='utf-8') as f:
            json.dump(self.benefits, f, indent=2)
        with open('card_benefits.json', 'w', encoding='utf-8') as f:
            json.dump(self.card_benefits, f, indent=2)
        with open('card_faces.json', 'w', encoding='utf-8') as f:
            json.dump(self.card_faces, f, indent=2)

    def get_cards_for_issuer(self, issuer_id):
        return [card for card in self.cards if card['issuerId'] == issuer_id]

    def get_benefits_for_card(self, card_id):
        benefit_ids = [cb['benefitId'] for cb in self.card_benefits if cb['cardId'] == card_id]
        return [b for b in self.benefits if b['id'] in benefit_ids]
    
    def get_faces_for_card(self, card_id):
        return [face for face in self.card_faces if face['cardId'] == card_id]

class App(customtkinter.CTk):
    def __init__(self):
        super().__init__()

        self.title("JSON Editor")
        self.geometry("1100x800")
        
        # Create a main scrollable frame
        main_frame = customtkinter.CTkScrollableFrame(self)
        main_frame.pack(fill="both", expand=True)

        self.data_manager = DataManager()
        self.current_card = None
        self.active_card_button = None
        self.card_buttons = {}
        self.detail_entries = {}
        self.benefit_entries = []

        # create tabview
        self.tab_view = customtkinter.CTkTabview(main_frame, width=1080)
        self.tab_view.pack(padx=10, pady=10)

        # create issuer tabs
        for issuer in self.data_manager.issuers:
            issuer_id = issuer['id']
            issuer_name = issuer['name']
            
            tab = self.tab_view.add(issuer_name)
            
            # Frame for horizontal scrolling of cards
            scrollable_frame = customtkinter.CTkScrollableFrame(tab, orientation="horizontal", border_width=2, border_color="gray")
            scrollable_frame.pack(fill="x", padx=5, pady=5)
            inner_frame = customtkinter.CTkFrame(scrollable_frame)
            inner_frame.pack(fill="both", expand=True)
            
            cards = self.data_manager.get_cards_for_issuer(issuer_id)
            
            row, col = 0, 0
            for card in cards:
                card_button = customtkinter.CTkButton(inner_frame, text=card['productName'], command=lambda c=card: self.show_card_details(c))
                card_button.grid(row=row, column=col, padx=10, pady=10)
                self.card_buttons[card['id']] = card_button
                
                col += 1
                if col % 5 == 0:
                    col = 0
                    row += 1

        # Frame for card details
        self.details_frame = customtkinter.CTkFrame(main_frame)
        self.details_frame.pack(fill="x", padx=15, pady=10)
        
        # Frame for card benefits
        self.benefits_frame = customtkinter.CTkFrame(main_frame)
        self.benefits_frame.pack(fill="x", padx=15, pady=10)

        # Frame for card faces
        self.card_faces_frame = customtkinter.CTkFrame(main_frame)
        self.card_faces_frame.pack(fill="x", padx=15, pady=10)

        # Save Button
        self.save_button = customtkinter.CTkButton(main_frame, text="Save Changes", command=self.save_card_details)
        self.save_button.pack(pady=10)


    def show_card_details(self, card):
        # Reset previous active button
        if self.active_card_button:
            self.active_card_button.configure(border_width=0)
        
        # Find and set new active button
        new_active_button = self.card_buttons.get(card['id'])
        if new_active_button:
            new_active_button.configure(border_width=2, border_color="blue")
            self.active_card_button = new_active_button
        
        self.current_card = card
        self.detail_entries = {}
        self.benefit_entries = []

        # Clear previous details
        for widget in self.details_frame.winfo_children():
            widget.destroy()
        for widget in self.benefits_frame.winfo_children():
            widget.destroy()

        # Populate card details
        details_row = 0
        for key, value in card.items():
            label = customtkinter.CTkLabel(self.details_frame, text=f"{key}:")
            label.grid(row=details_row, column=0, padx=10, pady=5, sticky="w")
            entry = customtkinter.CTkEntry(self.details_frame, width=300)
            entry.insert(0, str(value))
            entry.grid(row=details_row, column=1, padx=10, pady=5, sticky="ew")
            self.detail_entries[key] = entry
            details_row += 1
        
        # --- Populate card benefits ---
        benefits_header_frame = customtkinter.CTkFrame(self.benefits_frame)
        benefits_header_frame.pack(fill="x", padx=20, pady=5)
        customtkinter.CTkLabel(benefits_header_frame, text="Benefits:").pack(side="left", anchor="w", padx=10, pady=5)
        customtkinter.CTkButton(benefits_header_frame, text="Add New Benefit", command=self.add_new_benefit_form).pack(side="right", padx=10)

        benefits = self.data_manager.get_benefits_for_card(card['id'])
        
        for benefit in benefits:
            benefit_frame = customtkinter.CTkFrame(self.benefits_frame)
            benefit_frame.pack(fill="x", padx=20, pady=5)
            
            benefit_widgets = {}
            benefit_row = 0
            for key, value in benefit.items():
                if key == "merchant": # Skip merchant field
                    continue
                label = customtkinter.CTkLabel(benefit_frame, text=f"{key}:")
                label.grid(row=benefit_row, column=0, padx=10, pady=2, sticky="w")
                entry = customtkinter.CTkEntry(benefit_frame, width=250)
                # Handle category (list) for display
                if key == "category" and isinstance(value, list):
                    entry.insert(0, ", ".join(map(str, value)))
                else:
                    entry.insert(0, str(value) if value is not None else "")
                entry.grid(row=benefit_row, column=1, padx=10, pady=2, sticky="ew")
                benefit_widgets[key] = entry
                benefit_row += 1
            
            self.benefit_entries.append({
                "data": benefit,
                "widgets": benefit_widgets
            })

    def add_new_benefit_form(self):
        if not self.current_card:
            return

        new_benefit_template = {
            "id": f"new_{uuid.uuid4()}", # Temporary ID
            "type": "",
            "amount": 0.0,
            "cap": 0.0, # Changed to float for consistency
            "frequency": "",
            "category": [], # Empty list for new categories
            "enrollmentRequired": False,
            "startDateUtc": "",
            "endDateUtc": "",
            "notes": ""
        }

        benefit_frame = customtkinter.CTkFrame(self.benefits_frame, border_width=2, border_color="green")
        benefit_frame.pack(fill="x", padx=20, pady=5)
        
        benefit_widgets = {}
        benefit_row = 0
        for key, value in new_benefit_template.items():
            if key == "merchant": # Skip merchant field
                continue
            label = customtkinter.CTkLabel(benefit_frame, text=f"{key}:")
            label.grid(row=benefit_row, column=0, padx=10, pady=2, sticky="w")
            entry = customtkinter.CTkEntry(benefit_frame, width=250)
            # Handle category (list) for display
            if key == "category" and isinstance(value, list):
                entry.insert(0, ", ".join(map(str, value)))
            else:
                entry.insert(0, str(value) if value is not None else "")
            entry.grid(row=benefit_row, column=1, padx=10, pady=2, sticky="ew")
            benefit_widgets[key] = entry
            benefit_row += 1
        
        self.benefit_entries.append({
            "data": new_benefit_template,
            "widgets": benefit_widgets
        })

    def save_card_details(self):
        if self.current_card:
            card_id = self.current_card['id']
            # Save card details
            for key, entry_widget in self.detail_entries.items():
                new_value = entry_widget.get()
                original_value = self.current_card.get(key) # Use .get for safety
                if isinstance(original_value, int):
                    try: self.current_card[key] = int(new_value)
                    except (ValueError, TypeError): self.current_card[key] = 0 # Default to 0
                elif isinstance(original_value, float):
                    try: self.current_card[key] = float(new_value)
                    except (ValueError, TypeError): self.current_card[key] = 0.0 # Default to 0.0
                else: # Assume string for others
                    self.current_card[key] = new_value
            
            # Process and save benefit details
            for benefit_data_entry in list(self.benefit_entries): 
                is_new_benefit = benefit_data_entry['data']['id'].startswith("new_")

                processed_benefit_obj = {}
                for key, entry_widget in benefit_data_entry['widgets'].items():
                    value_str = entry_widget.get()
                    
                    if key == "id":
                        processed_benefit_obj[key] = value_str
                    elif key in ["amount", "cap"]:
                        try: processed_benefit_obj[key] = float(value_str)
                        except ValueError: processed_benefit_obj[key] = 0.0
                    elif key == "enrollmentRequired":
                        processed_benefit_obj[key] = value_str.lower() in ('true', '1', 'yes')
                    elif key == "category":
                        processed_benefit_obj[key] = [item.strip() for item in value_str.split(',') if item.strip()]
                    elif key in ["startDateUtc", "endDateUtc", "frequency", "type", "notes"]:
                        processed_benefit_obj[key] = value_str if value_str else None
                
                if is_new_benefit:
                    new_id_suffix = processed_benefit_obj.get('notes', processed_benefit_obj.get('type', ''))
                    new_id_suffix = "".join(c for c in new_id_suffix if c.isalnum()).lower()
                    if not new_id_suffix:
                        new_id_suffix = uuid.uuid4().hex[:8] # Fallback if notes/type is empty

                    final_new_benefit_id = f"{card_id}_{new_id_suffix}_{uuid.uuid4().hex[:4]}"
                    processed_benefit_obj['id'] = final_new_benefit_id
                    
                    self.data_manager.benefits.append(processed_benefit_obj)
                    
                    new_card_benefit_mapping = {
                        "id": f"{card_id}-{final_new_benefit_id}",
                        "cardId": card_id,
                        "benefitId": final_new_benefit_id
                    }
                    self.data_manager.card_benefits.append(new_card_benefit_mapping)
                else:
                    found = False
                    for i, b in enumerate(self.data_manager.benefits):
                        if b['id'] == processed_benefit_obj['id']:
                            self.data_manager.benefits[i] = processed_benefit_obj
                            found = True
                            break
                    if not found:
                        print(f"Warning: Benefit with ID '{processed_benefit_obj['id']}' not found. Adding it.")
                        self.data_manager.benefits.append(processed_benefit_obj)

            self.data_manager.save_data()
            self.show_card_details(self.current_card)
            print("Changes saved successfully!")


if __name__ == "__main__":
    app = App()
    app.mainloop()
