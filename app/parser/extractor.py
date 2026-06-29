from bs4 import BeautifulSoup


class CDSCOExtractor:

    def __init__(self, html):
        self.soup = BeautifulSoup(html, "lxml")

    def get_all_panels(self):
        """
        Returns all approval cards on the page.
        """
        return self.soup.find_all("div", class_="panel panel-info")

    def extract_panel(self, panel):
        """
        Extracts one approval card into a dictionary.
        """

        record = {}

        # ---------------- Heading ---------------- #

        heading = panel.find("div", class_="panel-heading")

        title = heading.find("h4").get_text(" ", strip=True)

        category = heading.find("button").get_text(strip=True)

        drug_name = title.replace(category, "").strip()

        record["category"] = category
        record["drug_name"] = drug_name

        # ---------------- Details ---------------- #

        legends = panel.find_all("legend")

        field_mapping = {
            "Approval Date": "approval_date",
            "Type": "type",
            "Composition": "composition",
            "Dosage": "dosage",
            "Indication": "indication",
            "Manufacturer Name": "manufacturer"
        }

        for legend in legends:
    
            label = legend.get_text(strip=True).replace(":", "").strip()

            print(f"Label found: '{label}'")

            value_div = legend.parent.find_next_sibling("div")

            if value_div:
                value = value_div.get_text(" ", strip=True)
            else:
                value = "NA"

            print(f"Value: '{value}'")

            if label == "Manufacturing Site Address":
                continue

            if label in field_mapping:
                print(f"Matched -> {field_mapping[label]}")
                record[field_mapping[label]] = value
            else:
                print("No Match!")

        return record

    def extract_all_records(self):
        """
        Extract all approval cards.
        """

        records = []

        panels = self.get_all_panels()

        print(f"Found {len(panels)} approvals")

        for panel in panels:
            records.append(self.extract_panel(panel))

        return records