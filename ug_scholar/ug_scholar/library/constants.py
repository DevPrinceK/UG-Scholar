
class SampleAuthorData:
    '''Sample Author Data'''
    # ['scholar', 'email', "college", 'school', 'department', 'rank']
    author_data = [
        {
            "scholar": "https://scholar.google.com/citations?user=Tpwr9vwAAAAJ&hl=en&oi=ao",
            "email": "ksadu-manu@ug.edu.gh",
            "college": "College of Basic and Applied Sciences",
            "school": "School of Physical and Mathematical Sciences",
            "department": "Computer Science",
            "rank": "Senior Lecturer"
        },
        {
            "scholar": "https://scholar.google.com/citations?hl=en&user=bSzu19wAAAAJ",
            "email": "wyaokumah@ug.edu.gh",
            "college": "College of Basic and Applied Sciences",
            "school": "School of Physical and Mathematical Sciences",
            "department": "Computer Science",
            "rank": "Professor"
        },
        {
            "scholar": "https://scholar.google.com/citations?hl=en&user=jgx_JBYAAAAJ",
            "email": "edansong@ug.edu.gh",
            "college": "College of Basic and Applied Sciences",
            "school": "School of Physical and Mathematical Sciences",
            "department": "Computer Science",
            "rank": "Senior Lecturer"
        },
        {
            "scholar": "https://scholar.google.com.au/citations?user=-q7bsWUAAAAJ&hl=en",
            "email": "revgyampo@ug.edu.gh",
            "college": "College of Humanities",
            "school": "School of Social Sciences",
            "department": "Political Science",
            "rank": "Professor"
        },
    ]
    
    def get_author_sample_data(self):
        return self.author_data

class UG:
    '''UG Constants'''
    
    # Faculties ranks in UG
    ranks = [
        "ASSISTANT LECTURER",
        "LECTURER",
        "SENIOR LECTURER",
        "FELLOW",
        "SENIOR RESEARCH FELLOW",
        "ASSOCIATE PROFESSOR",
        "PROFESSOR",
        "PROFESSOR EMERITUS",
        "PROFESSOR EMERITA"
    ]
    
    # colleges in UG
    colleges = [
            "College of Health Sciences",
            "College of Basic and Applied Sciences",
            "College of Education",
            "College of Humanities",
        ]
    
    # schools, institutions and centers in UG
    schools = [
    "Pan-African Doctoral Academy at the University of Ghana",
    "Institute of Applied Science and Technology",
    "Institute for Environment and Sanitation Studies",
    "Biotechnology Research Centre",
    "Forest and Horticultural Crop Research Centre (FOHCREC)",
    "Livestock and Poultry Research Centre (LIPREC)",
    "Soil and Irrigation Research Centre (SIREC)",
    "West Africa Centre for Crop Improvement",
    "West African Center for Cell Biology of Infectious Pathogens",
    "Center for Climate Change and Sustainability Studies(C3SS)",
    "Noguchi Memorial Institute for Medical Research",
    "Centre for Tropical, Clinical Pharmacology & Therapeutics",
    "West African Genetic Medicine Centre (WAGMC)",
    "Institute of African Studies",
    "Regional Institute for Population Studies",
    "Institute for Statistical, Social and Economic Research",
    "Maria Sibylla Merian Institute for Advanced Studies in Africa",
    "Centre for Gender Studies and Advocacy",
    "Centre for Migration Studies",
    "Centre for Social Policy Studies",
    "Centre for Urban Management Studies",
    "Centre for Asian Studies",
    "Centre for Latin American Studies",
    "Centre for Ageing Studies",
    "Centre for European Studies",
    "Centre for Remote Sensing and Geographical Information Systems",
    "Language Centre",
    "Legon Centre for International Affairs and Diplomacy",
    "Accra City Campus",
    "Remote Sensing and Geographical Information Systems Labs"
]
    
    departments = [
    "Family and Consumer Sciences",
    "Nutrition and Food Science",
    "Food Process Engineering",
    "Obstetrics and Gynecology",
    "French",
    "Oral and Maxillofacial Surgery",
    "Haematology",
    "Oral Pathology and Medicine",
    "Medical Pharmacology",
    "History",
    "Oral Biology",
    "Health Policy, Planning and Management",
    "Orthodontics and Paedodontics",
    "Information Studies",
    "Forest and Horticultural Crop Research Centre (FOHCREC)",
    "Pathology",
    "Marine and Fisheries Sciences",
    "Pharmaceutical Chemistry",
    "Mathematics",
    "Preventive and Community Dentistry",
    "Maternal and Child Health",
    "Population, Family and Reproduction Health",
    "Anaesthesia",
    "Archaeology and Heritage Studies",
    "Audiology, Speech and Language",
    "Biochemistry, Cell and Molecular Biology",
    "Chemical Pathology",
    "Biological, Environmental and Occupational Health",
    "Occupational Therapy",
    "Biomaterial Sciences",
    "Geography and Resource Development",
    "Health Services Management",
    "Biomedical Engineering",
    "Computer Engineering",
    "Biostatistics",
    "Finance",
    "Chemistry",
    "Accounting",
    "Child Health",
    "Marketing & Entrepreneurship",
    "Community Health",
    "Bacteriology",
    "Immunology",
    "Organisation and HR Management",
    "Public Administration and Health",
    "Public Health Nursing",
    "Communication Studies",
    "Adult Health",
    "Crop Science",
    "Veterinary Medicine",
    "Agricultural Economics and Agribusiness",
    "Dance",
    "Adult Education",
    "Distance Education",
    "Agricultural Engineering",
    "Plant and Environmental Biology",
    "Agricultural Extension",
    "Earth Science",
    "Anatomy",
    "Epidemiology and Disease Control",
    "Nursing and Midwifery"
    "Animal Science",
    "English",
    "Parasitology",
    "Medical Biochemistry",
    "Philosophy and Classics",
    "Medicine and Therapeutic",
    "Pharmacognosy and Herbal Medicine",
    "Mental Health Nursing",
    "Physical Education and Sports",
    "Medical Laboratory Sciences",
    "Physics",
    "Law",
    "Modern Languages",
    "Medicine",
    "Europeans Languages",
    "Physiology",
    "Materials Science and Engineering",
    "Physiotherapy",
    "Music",
    "Pharmaceutics and Microbiology",
    "Nutrition and Dietetics",
    "Pharmacy Practice and Clinical Pharmacy",
    "Political Science",
    "Sociology",
    "Soil Science",
    "Psychiatry",
    "Statistics",
    "Psychology",
    "Surgery",
    "Virology",
    "Pharmacology and Toxicology",
    "Teacher Education and Leadership",
    "Electron Microscopy and Histopathology",
    "Radiography",
    "Theatre",
    "Radiology",
    "Computer Science",
    "Restorative Dentistry",
    "Medical Microbiology",
    "Research, Education and Administration",
    "Operations and Management Information Systems",
    "Religions",
    "Animal Biology and Conservation Science",
    "Social and Behavioural Sciences",
    "Economics",
    "Social Work",
    "Societies and Cultures",
    "Linguistics"
]
    
    
    def get_colleges(self):
        return self.colleges
    
    def get_departments(self):
        return self.departments
    
    def get_schools(self):
        return self.schools
    
    def get_ranks(self):
        return self.ranks