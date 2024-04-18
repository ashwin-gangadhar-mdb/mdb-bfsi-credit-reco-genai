// components/Sidebar.js

import React, { useState } from 'react';
import styles from '../styles/sidebar.module.css';
import { H3, Body, Subtitle } from '@leafygreen-ui/typography';
import { NumberInput } from '@leafygreen-ui/number-input';
import Button from '@leafygreen-ui/button';
import Popup from '../components/Popup';
import axios from 'axios';
import Slider from 'rc-slider';
import 'rc-slider/assets/index.css';
import ProfileSlider from '../components/ProfileSlider';

// Name
// Age
// Occupation
// Annual_Income
// Monthly_Inhand_Salary
// Credit_Mix
// Credit_Utilization_Ratio
// Type_of_Loan
// Monthly_Balance
// Payment_Behaviour


const Sidebar = ({ profileInfo }) => {
  const [isPopupOpen, setPopupOpen] = useState(false);

  const [Name, setName] = useState(profileInfo.Name);
  const [Occupation, setOccupation] = useState(profileInfo.Occupation);
  const [Age, setAge] = useState(profileInfo.Age);
  const [Income, setIncome] = useState(profileInfo.Monthly_Inhand_Salary);
  const [Annual_Income, setAnnual_Income] = useState(profileInfo.Annual_Income);
  const [Credit_Mix, setCredit_Mix] = useState(profileInfo.Credit_Mix);
  const [Credit_Utilization_Ratio, setCredit_Utilization_Ratio] = useState(profileInfo.Credit_Utilization_Ratio);
  const [Type_of_Loan, setType_of_Loan] = useState(profileInfo.Type_of_Loan);
  const [Monthly_Balance, setMonthly_Balance] = useState(profileInfo.Monthly_Balance);
  const [Payment_Behaviour, setPayment_Behaviour] = useState(profileInfo.Payment_Behaviour);
  const [Interest_Rate , setInterest_Rate] = useState(profileInfo.Interest_Rate);
  const [Outstanding_Debt, setOutstanding_Debt] = useState(profileInfo.Outstanding_Debt);
  const [Num_Credit_Card, setNum_Credit_Card] = useState(profileInfo.Num_Credit_Card);
  const [Num_Bank_Accounts, setNum_Bank_Accounts] = useState(profileInfo.Num_Bank_Accounts);
  const [Total_EMI_per_month, setTotal_EMI_per_month] = useState(profileInfo.Total_EMI_per_month);
  const [Monthly_Inhand_Salary, setMonthly_Inhand_Salary] = useState(profileInfo.Monthly_Inhand_Salary);


  const setters = {
    age: setAge,
    income: setIncome,
    annualIncome : setAnnual_Income,
    creditMix : setCredit_Mix,
    creditUtilizationRatio : setCredit_Utilization_Ratio,
    typeOfLoan : setType_of_Loan,
    monthlyBalance : setMonthly_Balance,
    paymentBehaviour : setPayment_Behaviour,
    interestRate : setInterest_Rate,
    outstandingDebt : setOutstanding_Debt,
    numCreditCard : setNum_Credit_Card,
    numBankAccounts : setNum_Bank_Accounts,
    totalEMIperMonth : setTotal_EMI_per_month,
    monthlyInhandSalary : setMonthly_Inhand_Salary
  };

  const defaultSliderStyle = {
    track: { backgroundColor: 'green' },
    handle: { borderColor: 'white', backgroundColor: 'black' },
  };

  const handleSliderChange = (event, param) => {
    const setter = setters[param];
    if (setter) {
      setter(event);
    }
  };

  const handleClick = () => {
    setPopupOpen(true);
  };

  const handleClosePopup = () => {
    setPopupOpen(false);
  };

  const handleAge = (event) => {
    const { value } = event.target;
    setAge(value);
  };

  const handleIncome = (event) => {
    const { value } = event.target;
    setIncome(value);
  };

  const handleDependents = (event) => {
    const { value } = event.target;
    setDependents(value);
  };

  const handlePortfolio = (event) => {
    const { value } = event.target;
    setPortfolio(value);
  };

  const handleInvestments = (event) => {
    const { value } = event.target;
    setInvestments(value);
  };



  const handleSubmit = async () => {

    const userData = {
      ...(Interest_Rate !== null && { "Interest_Rate": parseFloat(Interest_Rate) }),
      ...(Outstanding_Debt !== null && { "Outstanding_Debt": parseFloat(Outstanding_Debt) }),
      ...(Num_Credit_Card !== null && { "Num_Credit_Card": parseInt(Num_Credit_Card, 10) }),
      ...(Num_Bank_Accounts !== null && { "Num_Bank_Accounts": parseInt(Num_Bank_Accounts, 10) }),
      ...(Total_EMI_per_month !== null && { "Total_EMI_per_month": parseFloat(Total_EMI_per_month) }),
      ...(Monthly_Inhand_Salary !== null && { "Monthly_Inhand_Salary": parseFloat(Monthly_Inhand_Salary) }),
    };
    console.log('Submitted user data:', userData);

    const clientId = localStorage.getItem('clientId');
    const filter = { "Customer_ID": parseInt(clientId, 10)}

    const body = { "filter": filter, "update": { $set: userData } };
    console.log('body:', body);

    const response = await axios.post('../api/updateOne', body);

    if (response.status === 200) {
      console.log('Record updated successfully:', response.data);
      // Close the popup
      setPopupOpen(false);
      window.location.reload();
    } else {
      console.log('Record updated unsuccessfully:', response.data);
    }
  }


  return (
    <div>
      {isPopupOpen && <div className="header-backdrop" />}
      {isPopupOpen && <div className="button-backdrop" />}
      <div className={styles.sidebar}>
        <div style={{display: "flex", flexDirection: "row", justifyContent: "space-around", marginBottom: "10%"}}>
          <img className={styles.profileImage} src={'/images/userAvatar.png'} alt="Profile" />
          {profileInfo && (
            <div style={{marginTop: "10%"}} >
              <H3> {profileInfo.Name}</H3>
              <Subtitle> {profileInfo.Occupation}</Subtitle>
              <Subtitle> {profileInfo.Age} years</Subtitle>
              <Subtitle >{profileInfo.ID}</Subtitle> 
            </div>
          
          )}
        </div>
        <div className={styles.profileDetails}>
          {profileInfo && (
            <>

              <div className={styles.profileItem}>
                <Body style={{ width: "20%" }}><strong>Interest Rate:&nbsp; </strong></Body>
                <Slider onChange={(event) => handleSliderChange(event, 'interestRate')}
                  styles={defaultSliderStyle}
                  defaultValue={Interest_Rate} style={{ width: "55%" }} />
                <Body baseFontSize={9} style={{ width: "10%" }}>{Interest_Rate}</Body>
              </div>

              <div className={styles.profileItem}>
                <Body style={{ width: "20%" }}><strong>Outstanding Debt:&nbsp;</strong></Body>
                <Slider max={10000} onChange={(event) => handleSliderChange(event, 'outstandingDebt')}
                  styles={defaultSliderStyle}
                  defaultValue={Outstanding_Debt} style={{ width: "55%" }} />
                <Body baseFontSize={9} style={{ width: "10%" }}>${Outstanding_Debt.toFixed(0)}</Body>
              </div>


              <div className={styles.profileItem}>
                <Body style={{ width: "20%" }}><strong>Num Credit Card:&nbsp;</strong></Body>
                <Slider max={20} onChange={(event) => handleSliderChange(event, 'numCreditCard')}
                  styles={defaultSliderStyle}
                  defaultValue={Num_Credit_Card} style={{ width: "55%" }} />
                <Body baseFontSize={9} style={{ width: "10%" }}>{Num_Credit_Card.toFixed(0)}</Body>
              </div>

              <div className={styles.profileItem}>
                <Body style={{ width: "20%" }}><strong>Num Bank Accounts:&nbsp;</strong></Body>
                <Slider max={20} onChange={(event) => handleSliderChange(event, 'numBankAccounts')}
                  styles={defaultSliderStyle}
                  defaultValue={Num_Bank_Accounts} style={{ width: "55%" }} />
                <Body baseFontSize={9} style={{ width: "10%" }}>{Num_Bank_Accounts.toFixed(0)}</Body>
              </div>

              <div className={styles.profileItem}>
                <Body style={{ width: "20%" }}><strong>Total EMI per month:&nbsp;</strong></Body>
                <Slider max={100000} onChange={(event) => handleSliderChange(event, 'totalEMIperMonth')}
                  styles={defaultSliderStyle}
                  defaultValue={Total_EMI_per_month} style={{ width: "55%" }} />
                <Body baseFontSize={9} style={{ width: "10%" }}>${Total_EMI_per_month.toFixed(0)}</Body>
              </div>

              <div className={styles.profileItem}>
                <Body style={{ width: "20%" }}><strong>Monthly Inhand Salary:&nbsp;</strong></Body>
                <Slider max={100000} onChange={(event) => handleSliderChange(event, 'monthlyInhandSalary')}
                  styles={defaultSliderStyle}
                  defaultValue={Monthly_Inhand_Salary} style={{ width: "55%" }} />
                <Body baseFontSize={9} style={{ width: "10%" }}>${Monthly_Inhand_Salary.toFixed(0)}</Body>
              </div>

              <br></br>
              <div className={styles.profileItem}>
                <Body style={{ width: "25%" }}><strong>Credit Mix:&nbsp;</strong></Body>
                <Body baseFontSize={9} style={{ width: "45%" }}>{Credit_Mix}</Body>
              </div>

              <div className={styles.profileItem}>
                <Body style={{ width: "25%" }}><strong>Type of Loan:&nbsp;</strong></Body>
                <Body baseFontSize={9} style={{ width: "45%" }}>{Type_of_Loan}</Body>
              </div>

              <div className={styles.profileItem}>
                <Body style={{ width: "25%" }}><strong>Payment Behaviour:&nbsp;</strong></Body>
                <Body baseFontSize={9} style={{ width: "45%" }}>{Payment_Behaviour}</Body>
              </div>
              

              <div className={styles.profileItem}>
                <Button style={{
                  marginTop: "35px",
                  width: "80%",
                }} onClick={handleSubmit}> Save Profile </Button>
              </div>

              <div style={{marginTop: "5em", display: "flex", flexDirection: "row", justifyContent: "space-around"}}>
                <Body style={{color: "dark-green"}}> Made with &hearts; by </Body>
                <Body> <a href="https://your-url.com" target="_blank" rel="noopener noreferrer">Ashwin Gangadhar</a> </Body>
                <Body> <a href="https://your-url.com" target="_blank" rel="noopener noreferrer">Paul Claret</a></Body>
                <Body> <a href="https://your-url.com" target="_blank" rel="noopener noreferrer">Utsav Talwar</a></Body>
              </div>
              
            </>
          )}
        </div>
      </div>
    </div>
  );
};

export default Sidebar;
