import Link from "next/link";
import ApplyNowButton from "@/app/components/school/ApplyNowButton";

const Footer = () => {
  return (
    <footer className="bg-midnight_text text-white">
      <div className="container mx-auto grid max-w-screen-xl gap-10 px-4 py-14 md:grid-cols-4">
        <div>
          <h4 className="mb-3 text-lg !text-white">British Opening Schools</h4>
          <p className="text-sm text-blue-100">Knowledge for skills</p>
        </div>
        <div>
          <h5 className="mb-3 text-base !text-white">Quick Links</h5>
          <div className="space-y-2 text-sm text-blue-100">
            <Link href="/academics" className="block hover:text-white">Academics</Link>
            <Link href="/admission" className="block hover:text-white">Admissions</Link>
            <Link href="/news" className="block hover:text-white">News</Link>
            <Link href="/contact-us" className="block hover:text-white">Contact</Link>
          </div>
        </div>
        <div>
          <h5 className="mb-3 text-base !text-white">Admissions</h5>
          <p className="text-sm text-blue-100">Start your application journey today.</p>
          <ApplyNowButton className="mt-4 inline-block rounded-lg bg-primary px-4 py-2 text-sm font-semibold text-white" />
        </div>
        <div>
          <h5 className="mb-3 text-base !text-white">Contact</h5>
          <p className="text-sm text-blue-100">P.O Box 120, Dar es Salaam- Mwenge ITV</p>
          <p className="mt-1 text-sm text-blue-100">255755400420,255655400420 </p>
          <p className="mt-1 text-sm text-blue-100">britishschooltz09@gmail.com</p>
        </div>
      </div>
      <div className="border-t border-blue-900 py-4 text-center text-xs text-blue-200">© {new Date().getFullYear()} The British Opening Schools. All rights reserved.</div>
    </footer>
  );
};

export default Footer;
