// pages/index.js
import React, { useEffect, useState } from 'react';
import Layout from '../components/Layout';
import Header from '../components/Header';
import Sidebar from '../components/Sidebar';
import { H1, H2, H3, Body } from '@leafygreen-ui/typography';
import TextWithImage from '../components/TextWithImage';
import { Tabs, Tab } from '@leafygreen-ui/tabs';


const HomePage = () => {
  const [data, setData] = useState(null);
  const [loading, setLoading] = useState(true);
  const [loading2, setLoading2] = useState(true);
  const [SecondTab, setSecondTab] = useState(true);
  const [selected, setSelected] = useState(0)
  const [explSets, setExplSets] = useState({ "userProfile": "" })
  const [recSets, setRecSets] = useState({ "product_suggestions": null })
  const [error, setError] = useState(false)
  const [health, setHealth] = useState(null)
  const labels = ["Repayment History", "Credit Utilization", "Credit History", "Net Credit", "Outstanding", "Credit Score"];

  useEffect(() => {
    if (typeof window !== 'undefined') {
      const clientId = localStorage.getItem('clientId');
      console.log('clientId', clientId);
      if (!clientId) {
        window.location.href = '/login';
        return;
      }
      fetchProfileData(parseInt(clientId, 10));
      fetchExpl(parseInt(clientId, 10));
    }

  }, []);

  useEffect(() => {
    if (explSets["userProfile"]) {
      fetchRec();
    }
  }, [explSets]);

  const fetchProfileData = async (clientId) => {
    try {
      const response = await fetch('/api/findOne', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          filter: { "Customer_ID": clientId },
        }),
      });

      if (!response.ok) {
        throw new Error(`Failed to fetch data. Status: ${response.status}`);
      }

      const jsonData = await response.json();

      console.log('jsonData', jsonData);
      if (!jsonData || Object.keys(jsonData).length === 0) {
        window.location.href = '/login';
        return;
      }
      setLoading(false);
      setData(jsonData);

    } catch (error) {
      console.error('Error fetching API data:', error);
      setLoading(false);
    }
  };


  const fetchExpl = async (clientId) => {
    try {
      const apiUrl = process.env.NEXT_PUBLIC_API_URL;
      const response = await fetch(`${apiUrl}/credit_score/${clientId}`, {
        method: 'GET',
        headers: {
          'Content-Type': 'application/json',
        }
      });
      const text = await response.json();
      setExplSets(text);
      setLoading2(false);
      console.log('text', text);
      setHealth(text.userCreditProfile);
      // if (text["approvalStatus"] == "Approved" ) {
      //   await setStatus(true);
      // } else {
      //   await setStatus(false);
      // }

      // poor -- red 
      // standard -- yellow
      // good -- green


    } catch (error) {
      setLoading2(false);
      console.error('Error fetching API response:', error);
    }
  };

  const fetchRec = async () => {
    try {
      const apiUrl = process.env.NEXT_PUBLIC_API_URL;
      const response = await fetch(`${apiUrl}/product_suggestions`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify(explSets)
      });
      const text = await response.json();
      setRecSets(text["productRecommendations"]);
      setSecondTab(false);

    } catch (error) {
      console.error('Error fetching API response:', error);
      setSecondTab(false);
    }
  };
  /*
  const textSet =  textSets ? textSets : {'explaination': 'Connexion error: please refresh the page\n1. toto\n  2. tata\n  3. tete\n ','product': {
    "No Connexion": " No Credit Card Recommended please refresh the page."
  } };

  /*
        <img
            src={key === "No Connexion" ? '/images/Error.png' : '/images/creditCard.png'}
            alt="Description"
            style={{ marginRight: '10px', maxWidth: '200px', borderRadius: '10px' }}
          />
  */
  const CHART_URL = process.env.NEXT_PUBLIC_CHART_URL;

  const textSet1WithIframe = (
    <div>
      {error ? (
        <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'left' }}>
          <img
            src={'/images/Error.png'}
            alt="Description"
            style={{ marginRight: '10px', maxWidth: '40px', borderRadius: '10px', marginTop: '10px' }}
          />
          <Body baseFontSize={16} as="pre" style={{ marginTop: '15px', fontSize: '19px', fontFamily: 'sans-serif' }}>
            Connexion error please refresh the page
          </Body>
        </div>
      ) : (
        <div></div>
      )}
      <Body baseFontSize={16} as="pre" style={{ wordWrap: 'break-word', overflowX: 'hidden', whiteSpace: 'pre-line', overflowX: 'hidden', fontSize: '19px', fontFamily: 'sans-serif', }} >
        {explSets["userProfile"]}
      </Body>
      {/* <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'center', marginTop: '20px' }}>
        <iframe
          style={{ background: '#FFFFFF', border: 'none', borderRadius: '8px', boxShadow: '0 2px 10px 0 rgba(70, 76, 79, .2)' }}
          width="400"
          height="200"
          src={CHART_URL}
        />
      </div> */}


<div style={{ display: 'flex', justifyContent: 'space-around', alignItems: 'center', flexWrap: 'wrap', marginTop: "40px" }}>
  {Array(6).fill().map((_, i) => (
    <React.Fragment key={i}>
      <div
        style={{
          background: '#FFFFFF',
          border: 'none',
          borderRadius: '8px',
          boxShadow: '0 2px 10px 0 rgba(70, 76, 79, .2)',
          width: '155px', // Adjusted width
          height: '85px', // Adjusted height
          display: 'flex',
          flexDirection: 'column',
          justifyContent: 'center',
          alignItems: 'center',
          margin: '10px' // Added margin
        }}
      >
        <H1>48</H1>
        <Body>{labels[i]}</Body>
      </div>
      {i < 4 && <div style={{ margin: '5px' }}>+</div>}
      {i == 4 && <div style={{ margin: '10px' }}>=</div>}
    </React.Fragment>
  ))}
</div>
    </div>
  );



  return (
    <div style={{ display: 'flex', flexDirection: 'column', height: '100vh' }}>
      {loading || loading2 ? (
        <div style={{ flex: 1, display: 'flex', alignItems: 'center', justifyContent: 'center', fontSize: '19px', fontFamily: 'sans-serif' }}>
          Loading...
        </div>
      ) : (
        <div style={{ flex: 1 }}>
          <Header />
          <Layout sidebar={<Sidebar profileInfo={data} />}
            mainContent={
              <div style={{ margin: '3%', marginTop: '30px' }}>
                <H3 style={{ display: 'inline' }}>Credit Health Status : </H3>
                {health === 'Poor' ? (
                  <div style={{ display: 'inline-block', borderRadius: '25px', background: '#FFCDC7', padding: '3px' }}>
                    <H3 style={{ color: '#970606', display: 'inline', marginBottom: '50px' }}>&nbsp;POOR&nbsp;</H3>
                  </div>
                ) : health === 'Standard' ? (
                  <div style={{ display: 'inline-block', borderRadius: '25px', background: '#C0FAE6', padding: '3px' }}>
                    <H3 style={{ color: '#00684A', display: 'inline', marginBottom: '50px' }}>&nbsp;STANDARD&nbsp;</H3>
                  </div>
                ) : (
                  <div style={{ display: 'inline-block', borderRadius: '25px', background: '#C0F9AD', padding: '3px' }}>
                    <H3 style={{ color: '#00684A', display: 'inline', marginBottom: '50px' }}>&nbsp;GOOD&nbsp;</H3>
                  </div>
                )}
                <Tabs setSelected={setSelected} selected={selected} baseFontSize={16}>
                  <Tab name="Status explanation" style={{ zIndex: 0 }}>{textSet1WithIframe}</Tab>
                  <Tab disabled={SecondTab} name="Product recommendations" style={{ zIndex: 0 }}>
                    <TextWithImage items={recSets} />
                  </Tab>
                </Tabs>
              </div>
            }
          />
        </div>
      )}
    </div>
  );

};

export default HomePage;
