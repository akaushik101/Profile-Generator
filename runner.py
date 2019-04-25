from comp_prof import Comp_prof



company = input("Input company ticker: ")

prof = Comp_prof(company)

prof.presentation = prof.run()
prof.presentation.save(str(company)+'.pptx')

