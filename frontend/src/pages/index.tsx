import ProjectForm from '../components/ProjectForm';

export default function Home() {
    return (
        <div className="container mx-auto px-4">
            <h1 className="text-xl font-bold text-center my-4">BREEAM Prosjektinnlevering</h1>
            <ProjectForm />
        </div>
    );
}
