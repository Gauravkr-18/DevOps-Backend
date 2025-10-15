from django.core.management.base import BaseCommand
from api.models import Category, Workshop


class Command(BaseCommand):
    help = 'Populate database with sample workshops and categories'

    def handle(self, *args, **kwargs):
        self.stdout.write('Creating categories...')
        
        # Create Categories
        categories_data = [
            {'name': 'Frontend', 'slug': 'frontend', 'icon': '', 
             'description': 'Modern frontend frameworks and libraries'},
            {'name': 'Backend', 'slug': 'backend', 'icon': '', 
             'description': 'Server-side development and APIs'},
            {'name': 'Mobile', 'slug': 'mobile', 'icon': '', 
             'description': 'Mobile app development'},
            {'name': 'DevOps', 'slug': 'devops', 'icon': '', 
             'description': 'Development and Operations practices'},
            {'name': 'AI/ML', 'slug': 'ai-ml', 'icon': '', 
             'description': 'Artificial Intelligence and Machine Learning'},
            {'name': 'Data Engineering', 'slug': 'data-engineering', 'icon': '', 
             'description': 'Data pipelines and processing'},
            {'name': 'Cloud', 'slug': 'cloud', 'icon': '', 
             'description': 'Cloud computing and services'},
            {'name': 'Cybersecurity', 'slug': 'cybersecurity', 'icon': '', 
             'description': 'Security practices and tools'},
        ]

        for cat_data in categories_data:
            category, created = Category.objects.get_or_create(
                slug=cat_data['slug'],
                defaults=cat_data
            )
            if created:
                self.stdout.write(self.style.SUCCESS(f'Created category: {category.name}'))

        self.stdout.write('Creating workshops...')

        # Create Workshops
        workshops_data = [
            {
                'title': 'React.js Workshop - 3 Days Intensive',
                'slug': 'reactjs-workshop',
                'description': 'Hands-On Training: React, Hooks, Routing & AI Chatbot - Build Modern UIs with React in just 3 days.',
                'category_slug': 'frontend',
                'difficulty': 'intermediate',
                'duration': '3 Days',
                'instructor': 'Sarah Johnson',
                'max_students': 30,
            },
            {
                'title': 'Angular Workshop',
                'slug': 'angular-workshop',
                'description': 'Learn to build robust, enterprise-scale applications with the Angular framework.',
                'category_slug': 'frontend',
                'difficulty': 'intermediate',
                'duration': '4 Days',
                'instructor': 'Mike Anderson',
                'max_students': 25,
            },
            {
                'title': 'Vue.js Workshop',
                'slug': 'vuejs-workshop',
                'description': 'Hands-On Training: Vue.js Workshop - Discover the progressive JavaScript framework for building intuitive user interfaces.',
                'category_slug': 'frontend',
                'difficulty': 'beginner',
                'duration': '3 Days',
                'instructor': 'Emma Davis',
                'max_students': 30,
            },
            {
                'title': 'Next.js Workshop',
                'slug': 'nextjs-workshop',
                'description': 'Explore server-side rendering, static site generation, and more with this React framework.',
                'category_slug': 'frontend',
                'difficulty': 'advanced',
                'duration': '2 Days',
                'instructor': 'John Smith',
                'max_students': 20,
            },
            {
                'title': 'Django REST Framework Workshop',
                'slug': 'django-rest-workshop',
                'description': 'Build powerful RESTful APIs with Django and Django REST Framework.',
                'category_slug': 'backend',
                'difficulty': 'intermediate',
                'duration': '4 Days',
                'instructor': 'Alex Chen',
                'max_students': 25,
            },
            {
                'title': 'Node.js & Express Workshop',
                'slug': 'nodejs-workshop',
                'description': 'Master server-side JavaScript development with Node.js and Express.',
                'category_slug': 'backend',
                'difficulty': 'beginner',
                'duration': '3 Days',
                'instructor': 'Maria Garcia',
                'max_students': 30,
            },
            {
                'title': 'Flutter Workshop',
                'slug': 'flutter-workshop',
                'description': 'Build beautiful, natively compiled applications for mobile from a single codebase.',
                'category_slug': 'mobile',
                'difficulty': 'intermediate',
                'duration': '5 Days',
                'instructor': 'David Lee',
                'max_students': 20,
            },
            {
                'title': 'React Native Workshop',
                'slug': 'react-native-workshop',
                'description': 'Create cross-platform mobile apps using React Native.',
                'category_slug': 'mobile',
                'difficulty': 'intermediate',
                'duration': '4 Days',
                'instructor': 'Lisa Brown',
                'max_students': 25,
            },
            {
                'title': 'Docker & Kubernetes Workshop',
                'slug': 'docker-kubernetes-workshop',
                'description': 'Master containerization and orchestration with Docker and Kubernetes.',
                'category_slug': 'devops',
                'difficulty': 'advanced',
                'duration': '5 Days',
                'instructor': 'Robert Wilson',
                'max_students': 20,
            },
            {
                'title': 'AWS Cloud Practitioner Workshop',
                'slug': 'aws-workshop',
                'description': 'Learn the fundamentals of Amazon Web Services and cloud computing.',
                'category_slug': 'cloud',
                'difficulty': 'beginner',
                'duration': '3 Days',
                'instructor': 'Jennifer Taylor',
                'max_students': 35,
            },
            {
                'title': 'Machine Learning with Python',
                'slug': 'ml-python-workshop',
                'description': 'Introduction to machine learning concepts and implementation using Python.',
                'category_slug': 'ai-ml',
                'difficulty': 'intermediate',
                'duration': '6 Days',
                'instructor': 'Dr. James Moore',
                'max_students': 25,
            },
            {
                'title': 'Data Engineering with Apache Spark',
                'slug': 'spark-workshop',
                'description': 'Build scalable data processing pipelines with Apache Spark.',
                'category_slug': 'data-engineering',
                'difficulty': 'advanced',
                'duration': '5 Days',
                'instructor': 'Patricia Martinez',
                'max_students': 20,
            },
            {
                'title': 'Ethical Hacking & Penetration Testing',
                'slug': 'ethical-hacking-workshop',
                'description': 'Learn cybersecurity fundamentals and ethical hacking techniques.',
                'category_slug': 'cybersecurity',
                'difficulty': 'advanced',
                'duration': '7 Days',
                'instructor': 'Chris Anderson',
                'max_students': 15,
            },
        ]

        for workshop_data in workshops_data:
            category_slug = workshop_data.pop('category_slug')
            category = Category.objects.get(slug=category_slug)
            
            workshop, created = Workshop.objects.get_or_create(
                slug=workshop_data['slug'],
                defaults={**workshop_data, 'category': category}
            )
            if created:
                self.stdout.write(self.style.SUCCESS(f'Created workshop: {workshop.title}'))

        self.stdout.write(self.style.SUCCESS('Database populated successfully!'))
