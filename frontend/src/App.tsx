import { useEffect } from "react";
import Dashboard from "./components/Dashboard";
import GaussianSplashBackground from "./utils/GaussianSplashBackground";

function App() {
    // 设置背景 WebGL 高斯效果
    useEffect(() => {
        const splashBackground = new GaussianSplashBackground();

        // 清理背景效果
        return () => {
            splashBackground.cleanup();
        };
    }, []);

    return (
        <div className="backdrop-blur-lg bg-white/60">
            <header className="fixed top-0 left-0 w-full z-50 bg-white/60 shadow-lg">
                <div className="max-w-7xl mx-auto py-10 px-4 sm:px-6 lg:px-8">
                    <h1 className="text-5xl text-center drop-shadow-lg">
                        CITANZ Membership Dashboard
                    </h1>
                </div>
            </header>
            <main>
                <div className="max-w-8xl mx-auto py-6 sm:px-6 lg:px-6 pt-32">
                    <Dashboard />
                </div>
            </main>
        </div>
    );
}

export default App;
