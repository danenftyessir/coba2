class MockRepository:
    def __init__(self):
        # data dummy dengan 10 CV yang lebih variatif
        self.mock_data = [
            {
                'applicant_id': 1,
                'name': 'Bryan P. Hutagalung',
                'cv_path': 'data/CV_Bryan.pdf',
                'email': 'bryan.p.hutagalung@gmail.com',
                'phone': '+6282211878972',
                'address': 'Jakarta, Indonesia',
                'linkedin_url': 'linkedin.com/in/bryan-hutagalung',
                'date_of_birth': '1998-05-25',
                'skills': 'Python, Java, SQL, React, Machine Learning, Docker, AWS, PostgreSQL, Django, Git',
                'work_experience': 'Software Engineer at Tech Corp (2020-Present)\nBackend Developer at StartUp Inc (2018-2020)',
                'education_history': 'Computer Science, Institut Teknologi Bandung (2018-2022)\nSMA 1 Jakarta (2015-2018)',
                'summary_overview': 'Experienced software engineer with focus on backend development and machine learning',
                'job_position': 'Software Engineer'
            },
            {
                'applicant_id': 2,
                'name': 'Danendra Shafi Athallah',
                'cv_path': 'data/CV_Danendra.pdf',
                'email': 'danendra.shafi@gmail.com',
                'phone': '+6281234567891',
                'address': 'Yogyakarta, Indonesia',
                'linkedin_url': 'linkedin.com/in/danendra-athallah',
                'date_of_birth': '1999-03-20',
                'skills': 'JavaScript, React, Node.js, MongoDB, AWS, Docker, Git, TypeScript, HTML, CSS',
                'work_experience': 'Full Stack Developer at StartUp Inc (2021-Present)\nFrontend Developer at Web Agency (2020-2021)',
                'education_history': 'Informatics Engineering, Institut Teknologi Bandung (2018-2022)\nSMA 3 Yogyakarta (2015-2018)',
                'summary_overview': 'Full stack developer specializing in modern web applications and cloud deployment',
                'job_position': 'Full Stack Developer'
            },
            {
                'applicant_id': 3,
                'name': 'Raihaan Perdana',
                'cv_path': 'data/CV_Raihaan.pdf',
                'email': 'raihaan.perdana@gmail.com',
                'phone': '+6281234567892',
                'address': 'Palembang, Indonesia',
                'linkedin_url': 'linkedin.com/in/raihaan-perdana',
                'date_of_birth': '1998-11-10',
                'skills': 'Python, C++, R, SQL, TensorFlow, PyTorch, Machine Learning, Kubernetes, Data Science, Pandas',
                'work_experience': 'Data Scientist at AI Company (2022-Present)\nSoftware Engineer at Tech Startup (2021-2022)',
                'education_history': 'Computer Science, Institut Teknologi Sepuluh Nopember (2018-2022)\nSMA 1 Palembang (2015-2018)',
                'summary_overview': 'Data scientist with expertise in machine learning, deep learning, and big data processing',
                'job_position': 'Data Scientist'
            },
            {
                'applicant_id': 4,
                'name': 'Alice Johnson',
                'cv_path': 'data/CV_Alice.pdf',
                'email': 'alice.johnson@email.com',
                'phone': '+6281234567893',
                'address': 'Bandung, Indonesia',
                'linkedin_url': 'linkedin.com/in/alice-johnson',
                'date_of_birth': '1997-07-15',
                'skills': 'Python, Django, Flask, PostgreSQL, Redis, Docker, Kubernetes, AWS, Linux, PyTest',
                'work_experience': 'Backend Developer at E-commerce Co (2020-Present)\nJunior Developer at Software House (2019-2020)',
                'education_history': 'Computer Engineering, Institut Teknologi Bandung (2017-2021)\nSMA Bandung (2014-2017)',
                'summary_overview': 'Backend developer experienced in building scalable web applications and APIs',
                'job_position': 'Backend Developer'
            },
            {
                'applicant_id': 5,
                'name': 'Bob Smith',
                'cv_path': 'data/CV_Bob.pdf',
                'email': 'bob.smith@email.com',
                'phone': '+6281234567894',
                'address': 'Surabaya, Indonesia',
                'linkedin_url': 'linkedin.com/in/bob-smith',
                'date_of_birth': '1996-12-03',
                'skills': 'Java, Spring Boot, MySQL, React, Angular, Docker, Kubernetes, Maven, Gradle, Microservices',
                'work_experience': 'Senior Java Developer at Banking Corp (2021-Present)\nJava Developer at Fintech Startup (2019-2021)',
                'education_history': 'Software Engineering, Universitas Airlangga (2016-2020)\nSMA Surabaya (2013-2016)',
                'summary_overview': 'Senior Java developer with expertise in enterprise applications and microservices',
                'job_position': 'Java Developer'
            },
            {
                'applicant_id': 6,
                'name': 'Catherine Lee',
                'cv_path': 'data/CV_Catherine.pdf',
                'email': 'catherine.lee@email.com',
                'phone': '+6281234567895',
                'address': 'Medan, Indonesia',
                'linkedin_url': 'linkedin.com/in/catherine-lee',
                'date_of_birth': '1999-09-12',
                'skills': 'Vue.js, Nuxt.js, JavaScript, TypeScript, Node.js, MongoDB, Firebase, GraphQL, Tailwind CSS',
                'work_experience': 'Frontend Developer at Digital Agency (2022-Present)\nJunior Frontend Developer at StartUp (2021-2022)',
                'education_history': 'Information Systems, Universitas Sumatera Utara (2019-2023)\nSMA 2 Medan (2016-2019)',
                'summary_overview': 'Creative frontend developer with passion for user experience and modern web technologies',
                'job_position': 'Frontend Developer'
            },
            {
                'applicant_id': 7,
                'name': 'David Chen',
                'cv_path': 'data/CV_David.pdf',
                'email': 'david.chen@email.com',
                'phone': '+6281234567896',
                'address': 'Semarang, Indonesia',
                'linkedin_url': 'linkedin.com/in/david-chen',
                'date_of_birth': '1997-02-28',
                'skills': 'DevOps, AWS, Azure, Terraform, Jenkins, Docker, Kubernetes, Linux, Ansible, Monitoring',
                'work_experience': 'DevOps Engineer at Cloud Company (2021-Present)\nSystem Administrator at Tech Corp (2019-2021)',
                'education_history': 'Computer Engineering, Universitas Diponegoro (2017-2021)\nSMA 1 Semarang (2014-2017)',
                'summary_overview': 'DevOps engineer specializing in cloud infrastructure and automation',
                'job_position': 'DevOps Engineer'
            },
            {
                'applicant_id': 8,
                'name': 'Elena Rodriguez',
                'cv_path': 'data/CV_Elena.pdf',
                'email': 'elena.rodriguez@email.com',
                'phone': '+6281234567897',
                'address': 'Malang, Indonesia',
                'linkedin_url': 'linkedin.com/in/elena-rodriguez',
                'date_of_birth': '1998-06-18',
                'skills': 'React Native, Flutter, Dart, Swift, Kotlin, Java, Firebase, SQLite, API Integration, Mobile UI/UX',
                'work_experience': 'Mobile Developer at App Studio (2022-Present)\nJunior Mobile Developer at Digital Agency (2020-2022)',
                'education_history': 'Informatics, Universitas Brawijaya (2018-2022)\nSMA 3 Malang (2015-2018)',
                'summary_overview': 'Mobile developer with expertise in cross-platform app development',
                'job_position': 'Mobile Developer'
            },
            {
                'applicant_id': 9,
                'name': 'Faisal Ahmad',
                'cv_path': 'data/CV_Faisal.pdf',
                'email': 'faisal.ahmad@email.com',
                'phone': '+6281234567898',
                'address': 'Makassar, Indonesia',
                'linkedin_url': 'linkedin.com/in/faisal-ahmad',
                'date_of_birth': '1996-10-05',
                'skills': 'PHP, Laravel, CodeIgniter, MySQL, PostgreSQL, Redis, JavaScript, jQuery, Bootstrap, REST API',
                'work_experience': 'Senior PHP Developer at Web Agency (2020-Present)\nPHP Developer at Local Company (2018-2020)',
                'education_history': 'Information Technology, Universitas Hasanuddin (2016-2020)\nSMA 1 Makassar (2013-2016)',
                'summary_overview': 'Senior PHP developer with strong background in web application development',
                'job_position': 'PHP Developer'
            },
            {
                'applicant_id': 10,
                'name': 'Grace Tan',
                'cv_path': 'data/CV_Grace.pdf',
                'email': 'grace.tan@email.com',
                'phone': '+6281234567899',
                'address': 'Batam, Indonesia',
                'linkedin_url': 'linkedin.com/in/grace-tan',
                'date_of_birth': '1999-04-22',
                'skills': 'UI/UX Design, Figma, Adobe XD, Sketch, Photoshop, Illustrator, Prototyping, User Research, Wireframing',
                'work_experience': 'UI/UX Designer at Design Studio (2022-Present)\nJunior Designer at Creative Agency (2021-2022)',
                'education_history': 'Visual Communication Design, Universitas Multimedia Nusantara (2019-2023)\nSMA Batam (2016-2019)',
                'summary_overview': 'Creative UI/UX designer focused on user-centered design and digital experiences',
                'job_position': 'UI/UX Designer'
            }
        ]

    def get_all_cvs(self):
        """ambil semua cv dari database - format untuk search"""
        return [
            {
                'applicant_id': cv['applicant_id'],
                'name': cv['name'],
                'cv_path': cv['cv_path'],
                'email': cv['email'],
                'phone': cv['phone'],
                'skills': cv['skills'],
                'job_position': cv['job_position']
            }
            for cv in self.mock_data
        ]

    def get_applicant_by_id(self, applicant_id):
        """ambil data lengkap applicant berdasarkan id"""
        for cv in self.mock_data:
            if cv['applicant_id'] == applicant_id:
                return cv
        return None

    def search_applicants(self, keyword):
        """cari applicant berdasarkan keyword - basic implementation"""
        results = []
        keyword_lower = keyword.lower()
        
        for cv in self.mock_data:
            # cari di nama, skills, work experience
            searchable_text = f"{cv['name']} {cv['skills']} {cv['work_experience']}".lower()
            
            if keyword_lower in searchable_text:
                results.append({
                    'applicant_id': cv['applicant_id'],
                    'name': cv['name'],
                    'email': cv['email'],
                    'skills': cv['skills'],
                    'cv_path': cv['cv_path']
                })
        
        return results

    def save_applicant(self, applicant_data):
        """simpan atau update data applicant"""
        print(f"💾 [MOCK] Saving applicant: {applicant_data.get('name', 'Unknown')}")
        return True

    def delete_applicant(self, applicant_id):
        """hapus data applicant"""
        print(f"🗑️ [MOCK] Deleting applicant ID: {applicant_id}")
        return True

    def get_statistics(self):
        """ambil statistik database"""
        return {
            'total_applicants': len(self.mock_data),
            'total_applications': len(self.mock_data)
        }