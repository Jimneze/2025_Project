# Project 2025

***Title:*** Cybersecurity Risks in Cloud Adoption: A Critical Review of Common Threats and Preventive Measures

## Vulnerabilities

- **Multi-Factor_Authentication (MFA)**
- prevent unauthorized login
- Solution: Use of django otp 

- **Brute Force Attack**
- guess password and credentials repeatedly
- Solution: use security to groups to allow ssh certificates from only known IP addresses, and implement Multifactor authentication for passwords

- **SQL Injection**
- using sql queries in requests to access database
- Solution: use of django ORM models to access database, preventing driect access

- **Priviledge Escalation**
- exploiting loose access priviledges to gain administrative rights
- Solution: Apply principle of least priviledge on iam roles & enable AWS Cloudtrail

- **Man in the Middle**
- Insecure http requests (Man in the middle): insecure host url: http://13.48.134.225
- Solution: use of elastic load balancer: 

- **DDoS Denial of Service**
- Flooding the server with request with the intention of taking it down
- Solution: use of elastic load balancer: 

- **Zero Trust Implementation**
- Requiring authentication for all processes
- Solution: using JWT token authentication with token lifetime of 60 minutes and a refresh lifetime of 7 days

## TO DO
- [x] build auth section
- [x] build todo section
- [x] connect aws rds database
- [x] connect aws s3 bucket
- [ ] deploy on fargate
- [x] deploy on ec2 instance
- [ ] Test security of both apps
- [ ] deploy on azure (if possible)
